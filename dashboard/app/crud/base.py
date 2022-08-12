from loguru import logger
from pydantic import BaseModel
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from dashboard.db.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD基础方法
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_title(self, db: Session, title: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.title == title).first()

    def get_multi(self,
                  db: Session,
                  *,
                  skip: int = 0,
                  limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def filter_page_size_order(self, query_info, query_):
        if query_info['page'] and query_info['page_size']:
            start = (int(query_info['page']) - 1) * int(
                query_info['page_size'])
            if query_info['order_by']:
                if '-' in query_info['order_by']:
                    key = (query_info['order_by'].split('-'))[1]
                    _tuple_list = query_.order_by(desc(key)).limit(
                        int(query_info['page_size'])).offset(start)
                else:
                    _tuple_list = query_.order_by(
                        query_info['order_by']).limit(
                            int(query_info['page_size'])).offset(start)
            else:
                _tuple_list = query_.limit(int(
                    query_info['page_size'])).offset(start)
        else:
            _tuple_list = query_.all()
        return _tuple_list

    def get_filter_base(self,
                        db: Session,
                        *,
                        query_info: dict = None,
                        id=None,
                        status=None):
        query_ = None
        if query_info:
            if 'and' in query_info and query_info['and']:
                #将筛选条件为空的去除
                query_info['and'] = {
                    item: query_info['and'][item]
                    for item in query_info['and'] if query_info['and'][item]
                }
                if 'like' in query_info and query_info['like']:
                    if 'id' in query_info['and']:
                        del query_info['and']['id']
                    query_curd = [
                        getattr(self.model, item).like("%{0}%".format(
                            query_info['and'][item]))
                        for item in query_info['and']
                        if query_info['and'][item]
                        if item not in ['output_path']
                        if getattr(self.model, item, None)
                    ]
                else:
                    query_curd = [
                        getattr(self.model, item) == query_info['and'][item]
                        for item in query_info['and']
                        if query_info['and'][item]
                        if getattr(self.model, item, None)
                    ]
                if 'time_range' in query_info and query_info['time_range']:
                    query_ = db.query(self.model).filter(
                        and_(*query_curd)).filter(
                            and_(
                                self.model.createTime >=
                                query_info['time_range']['create_st'],
                                self.model.createTime <=
                                query_info['time_range']['create_et']))
                else:
                    query_ = db.query(self.model).filter(and_(*query_curd))
            else:
                query_ = db.query(self.model)
            querys_count = len(query_.all())
            return query_, querys_count
        else:
            if id:
                results = db.query(self.model).filter(self.model.id == id)
                return results, 1
            else:
                results = db.query(self.model)
                return results, len(results)

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        if not isinstance(obj_in, dict):
            obj_in_data = obj_in.dict()
        else:
            obj_in_data = obj_in
        obj_in_data = {item: obj_in_data[item] for item in obj_in_data if obj_in_data and obj_in_data[item] != ''}
        try:
            db_obj = self.model(**obj_in_data)  # type: ignore
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            logger.debug(e)
            db.rollback()
            db_obj = None
        finally:
            db.close()
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType,
               obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        try:
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            logger.debug(e)
            db.rollback()
            db_obj = None
        finally:
            db.close()
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        try:
            db_obj = db.query(self.model).get(id)
            db.delete(db_obj)
            db.commit()
        except Exception as e:
            logger.debug(e)
            db.rollback()
            db_obj = None
        finally:
            db.close()
        return db_obj
