from loguru import logger
from sqlalchemy import desc
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from dashboard.app.crud.base import CRUDBase
from dashboard.app.resources import strings as base
from dashboard.app.common.utils import return_data_type
from dashboard.app.models.user import Roles, Permissions, RolesPermission
from dashboard.app.schemas.role_auth import RoleCreate, RoleUpdate, \
    PermissionsCreate, PermissionsUpdate

class CRUDRoles(CRUDBase[Roles, RoleCreate, RoleUpdate]):

    def get_data_count(self, db: Session):
        return db.query(self.model).count()

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
    def get_filter(self, db: Session, *, query_info= {}, id=None):
        query_, querys_count = self.get_filter_base(db=db,query_info=query_info)
        _tuple_list = self.filter_page_size_order(query_info, query_)
        data = [item.to_dict() for item in _tuple_list]
        return data, querys_count



    def create(self, db: Session, *, obj_in: RoleCreate) -> Roles:

        if not isinstance(obj_in, dict):
            obj_in_data = jsonable_encoder(obj_in)
        else:
            obj_in_data = obj_in
        pers_list = obj_in_data.pop("pers_list")
        try:
            db_obj = self.model(**obj_in_data)  # type: ignore
            db.add(db_obj)
            db.flush()
            create_list = []
            for item in pers_list:
                obj_sql = RolesPermission(roleId=db_obj.id, permissionId=int(item))
                create_list.append(obj_sql)
            db.add_all(create_list)
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            logger.debug(e)
            db_obj = None
            db.rollback()
        finally:
            db.close()
        return db_obj


    def update_(self, db:Session, info: RoleUpdate):
        if not isinstance(info, dict):
            info = info.dict(exclude_unset=True)
        if 'id' not in info:
            return None
        db_update = db.query(Roles).filter_by(id=info['id']).first()
        pers_list = info.pop("pers_list")
        if db_update:
            try:
                info_data = {item: info[item] for item in info if item not in ['id'] if info[item] is not None if info[item] != db_update.to_dict()[item] }
                for k, v in info_data.items():
                    setattr(db_update, k, v)
                relation_db = db.query(RolesPermission).filter(RolesPermission.roleId == info['id'])
                if pers_list != None:
                    if len(pers_list) == 0:
                        if relation_db.all():
                            relation_db.delete()
                    if len(pers_list) > 0:
                        if relation_db.all():
                            relation_db.delete()
                        create_list = []
                        for item in pers_list:
                            obj_sql = RolesPermission(roleId=info['id'], permissionId=int(item))
                            create_list.append(obj_sql)
                        db.add_all(create_list)
                db.commit()
                # db.flush()
                db.refresh(db_update)
                return db_update
            except Exception as e:
                logger.debug(e)
                db.rollback()
                db_update= None
            finally:
                db.close()
            return db_update
        else:
            return None

    #删除Roles表;
    #删除RolesPermission关系
    def delete_(self, db:Session, id: int=None):
        if not id:
            return None
        db_delete = db.query(Roles).filter_by(id= id)

        if db_delete.first():
            try:
                db_delete.delete()
                role_per = db.query(RolesPermission).filter_by(roleId= id)
                if role_per.all():
                    role_per.delete()
                db.commit()
                return db_delete
            except Exception as e:
                logger.debug(e)
                db.rollback()
                db_update = None
            finally:
                db.close()
            return db_update
        else:
            return None

    def get_relation_per(self,db: Session, obj):
        middle = db.query(RolesPermission).filter(RolesPermission.roleId == obj['id']).all()
        per_id_list = [item.permissionId for item in middle]
        per_set_list = [db.query(Permissions).filter(Permissions.id == item).first() for item in
                        per_id_list]
        per_dict_list = return_data_type(per_set_list)['list']
        return per_dict_list




class CRUDPermissions(CRUDBase[Permissions, PermissionsCreate, PermissionsUpdate]):
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
    def get_(self, db: Session, key):
        data = db.query(Permissions).filter_by(key=key).first()
        return data

    def get_data_total(self, db: Session):
        data = db.query(Permissions).count()
        return data

    def get_filter(self, db: Session, *, query_info= {}, id=None, status= None):
        query_, querys_count = self.get_filter_base(db=db,query_info=query_info)
        if status in base.Roles_deleted_list:
            query_ = query_.filter(Permissions.deleted == status)
            querys_count = len(query_.all())
        if query_info['page'] and query_info['page_size']:
            start = (int(query_info['page']) - 1) * int(query_info['page_size'])
            if query_info['order_by']:
                if '-' in query_info['order_by']:
                    key = (query_info['order_by'].split('-'))[1]
                    _tuple_list = query_.order_by(desc(key)).limit(int(query_info['page_size'])).offset(start)
                else:
                    _tuple_list = query_.order_by(query_info['order_by']).limit(int(query_info['page_size'])).offset(
                        start)
            else:
                _tuple_list = query_.limit(int(query_info['page_size'])).offset(start)
        else:
            _tuple_list = query_.all()
        data = [item.to_dict() for item in _tuple_list]
        return data, querys_count


    def create_(self, db: Session, *, obj_in: PermissionsCreate) -> Permissions:

        if not isinstance(obj_in, dict):
            obj_in_data = jsonable_encoder(obj_in)
        else:
            obj_in_data = obj_in
        try:
            db_obj = self.model(**obj_in_data)  # type: ignore
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            logger.debug(e)
            db_obj = None
        return db_obj


    def update_(self, db:Session, info: PermissionsUpdate):
        if not isinstance(info, dict):
            info = info.dict(exclude_unset=True)
        if 'id' not in info:
            return None
        db_update = db.query(Permissions).filter_by(id=info['id']).first()
        try:
            if db_update:
                info_data = {item: info[item] for item in info if item not in ['id'] if info[item] is not None if info[item] != db_update.to_dict()[item] }
                for k, v in info_data.items():
                    setattr(db_update, k, v)
                db.commit()
                db.refresh(db_update)
                return db_update
            else:
                return None
        except Exception as e:
            logger.debug(e)
            return None

    #删除Permissions数据
    #删除RolesPermission数据
    def delete_(self, db:Session, id:int= None):

        if not id:
            return None
        db_delete = db.query(Permissions).filter_by(id=id)
        role_per = db.query(RolesPermission).filter_by(permissionId= id)
        try:
            if db_delete.first():
                db_delete.delete()
                if role_per.first():
                    role_per.delete()
                db.commit()
                # db.flush()
                return db_delete
            else:
                return None
        except Exception as e:
            logger.debug(e)
            db.rollback()
        finally:
            db.close()


crud_role = CRUDRoles(Roles)
crud_per = CRUDPermissions(Permissions)
