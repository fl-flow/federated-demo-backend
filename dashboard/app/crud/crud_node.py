from typing import Any
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from dashboard.app.crud.base import CRUDBase
from dashboard.app.common.utils import get_uuid
from dashboard.app.resources import strings as base
from dashboard.app.models.user import WebsitNode, Roles
from dashboard.app.schemas import NodeCreate, NodeUpdate


class CRUDNode(CRUDBase[WebsitNode, NodeCreate, NodeUpdate]):
    """
    query_info={
    'and':{
    'id':1, 'filed1':xxx, 'filed2':xxx,
    },
    'time_range':{'create_st': '2020-01-01 12:12:20','create_et': '2020-01-20 12:50:30'}
    page: 1
    page_size: 10,
    order_by: str='id'
    like: 0 or 1
    }
    """
    def get_(self, db: Session, code: Any):
        return db.query(self.model).filter(self.model.code == code).first()

    def get_data_count(self, db: Session):
        return db.query(self.model).count()


    def get_filter(self, db: Session, *, query_info= {}, id=None, flag=None):
        query_, querys_count = self.get_filter_base(db=db, query_info=query_info)
        if flag in base.Roles_deleted_list:
            query_ = query_.filter(self.model.flag == flag)
        # querys_count = len(query_.all())
        querys_count = query_.count()
        print(querys_count)
        #分页
        _tuple_list = self.filter_page_size_order(query_info=query_info, query_=query_)
        data = [item.to_dict() for item in _tuple_list]
        return data, querys_count


    def create_(self, db: Session, *, obj_in: NodeCreate) -> WebsitNode:

        if not isinstance(obj_in, dict):
            obj_in_data = jsonable_encoder(obj_in)
        else:
            obj_in_data = obj_in
        obj_in_data['code'] = get_uuid()
        try:
            db_obj = self.model(**obj_in_data)  # type: ignore
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            print(e)
            db.rollback()
            db_obj = None
        finally:
            db.close()
        return db_obj


    def update_(self, db:Session, info: NodeUpdate):
        if not isinstance(info, dict):
            info = info.dict(exclude_unset=True)
        if 'id' not in info:
            return None
        # roleIds = info.pop('roleIds')
        db_update = db.query(WebsitNode).filter_by(id=info['id']).first()
        if db_update:
            info_data = {item: info[item] for item in info if item not in ['Node_id'] if info[item] is not None if info[item] != db_update.to_dict()[item]}
            for k, v in info_data.items():
                setattr(db_update, k, v)
            try:
                db.commit()
                # db.flush()
                db.refresh(db_update)
            except Exception as e:
                db.rollback()
                db_update = None
            finally:
                db.close()
            return db_update
        else:
            return None


    def get_relation_roles(self, db: Session, obj_dict):
        middle = db.query(Roles).filter(Roles.code == obj_dict['code']).all()
        roles_list = [item.to_dict() for item in middle]
        return roles_list



crud_node = CRUDNode(WebsitNode)
