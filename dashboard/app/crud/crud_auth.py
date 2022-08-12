from typing import Any

from loguru import logger
from sqlalchemy.orm import Session

from dashboard.app.core.security import YunAuthJWT
from dashboard.app.crud.base import CRUDBase
from dashboard.app.models.user import Authentication
from dashboard.app.schemas import AuthCreate, AuthUpdate


class CRUDAuth(CRUDBase[Authentication, AuthCreate, AuthUpdate]):
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
    def get_(self, db: Session, appKey: Any):
        return db.query(self.model).filter(self.model.appKey == appKey).first()

    def get_filter(self, db: Session, *, query_info= {}):
        query_, querys_count = self.get_filter_base(db=db, query_info=query_info)
        querys_count = query_.count()
        #分页
        _tuple_list = self.filter_page_size_order(query_info=query_info, query_=query_)
        data = [item.to_dict() for item in _tuple_list]
        return data, querys_count

    def create_(self, db: Session,  *, obj_in: AuthCreate) -> Authentication:
        obj_in_data = obj_in.dict()
        hash_password = YunAuthJWT().get_password_hash(obj_in_data['appSecret'])
        obj_in_data['appSecret'] = hash_password
        try:
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            logger.debug(e)
            db_obj = None
        return db_obj


    def update_(self, db:Session, info: AuthUpdate):
        if not isinstance(info, dict):
            info = info.dict(exclude_unset=True)
        if 'id' not in info:
            return None
        # roleIds = info.pop('roleIds')
        db_update = db.query(self.model).filter_by(id=info['id']).first()
        if db_update:
            info_data = {item: info[item] for item in info if item not in ['id'] if info[item] is not None if
                         info[item] != db_update.to_dict()[item]}
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

crud_auth = CRUDAuth(Authentication)
