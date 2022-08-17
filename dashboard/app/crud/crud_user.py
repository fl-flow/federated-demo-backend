from loguru import logger
from typing import Optional
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from dashboard.app.core.security import YunAuthJWT
from dashboard.app.crud.base import CRUDBase
from dashboard.app.resources import strings as base
from dashboard.app.models.user import Users, RolesPermission, Permissions, UsersRoles
from dashboard.app.schemas.user import UserCreate, UserUpdate, UserAddUser


class CRUDUser(CRUDBase[Users, UserCreate, UserUpdate]):
    def get_data_count(self, db: Session) -> Optional[Users]:
        return db.query(Users).count()

    def get_by_email(self, db: Session, *, email: str) -> Optional[Users]:
        return db.query(Users).filter(Users.userEmail == email).first()

    def get_by_phoneNumber(self, db: Session, *, phoneNumber: str) -> Optional[Users]:
        return db.query(Users).filter(Users.phoneNumber == phoneNumber).first()

    def get_filter(self, db: Session, *, query_info: dict, flag=None, id=None):
        query_, querys_count = self.get_filter_base(db=db, query_info=query_info)
        if flag in base.Users_status_list:
            query_ = query_.filter(Users.flag == flag)
        querys_count = query_.count()
        print(querys_count)
        #分页
        _tuple_list = self.filter_page_size_order(query_info=query_info, query_=query_)
        data = [item.to_dict() for item in _tuple_list]
        return data, querys_count


    def create(self, db: Session,  *, obj_in: UserCreate) -> Users:

        if not isinstance(obj_in, dict):
            obj_in_data = jsonable_encoder(obj_in)
        else:
            obj_in_data = obj_in
        hash_password = YunAuthJWT().get_password_hash(obj_in_data['password'])
        obj_in_data['password'] = hash_password
        obj_in_data['ownerUser'] = 0
        try:
            db_obj = Users(**obj_in_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            logger.debug(e)
            db_obj = None
        return db_obj

    def create_newuser(self, db: Session, *, obj_in: UserAddUser) -> Users:

        if not isinstance(obj_in, dict):
            obj_in_data = jsonable_encoder(obj_in)
        else:
            obj_in_data = obj_in
        roles = obj_in_data.pop("roles")
        hash_password = YunAuthJWT().get_password_hash(obj_in['password'])
        obj_in_data['password'] = hash_password
        print(obj_in_data,2222222222)
        middle_list = None
        try:
            db_obj = self.model(**obj_in_data)  # type: ignore
            db.add(db_obj)
            db.flush()
            if roles:
                middle_list = []
                for item in roles:
                    middle_list.append(
                        UsersRoles(userId=db_obj.id, roleId=int(item)))
                db.add_all(middle_list)
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            logger.debug(str(e))
            db.rollback()
            db_obj = None
            middle_list = None
        finally:
            db.close()
        return db_obj, middle_list

    def update_(self, db:Session, info: UserUpdate):
        if not isinstance(info, dict):
            info = info.dict(exclude_unset=True)
        if 'id' not in info['info']:
            return None
        db_update = db.query(Users).filter_by(id=info['info']['id']).first()
        if "roles" in info['info']:
            roles = info['info'].pop("roles")
        else:
            roles = None
        if db_update:
            try:
                info_data = {item: info['info'][item] for item in info['info'] if item not in ['id'] if info['info'][item]
                             is not None if info['info'][item] != db_update.to_dict()[item] }
                if 'password' in info_data:
                    if info_data['password']:
                        hash_password = YunAuthJWT().get_password_hash(info_data['password'])
                        info_data['password'] = hash_password
                for k, v in info_data.items():
                    setattr(db_update, k, v)

                if roles != None:
                    relation_db = db.query(UsersRoles).filter(UsersRoles.userId == info['info']['id'])
                    if len(roles) == 0:
                        relation_db.delete()
                    if len(roles) > 0:
                        relation_db.delete()
                        middle_list = []
                        for item in roles:
                            middle_list.append(UsersRoles(roleId= int(item), userId=info['info']['id']))
                        db.add_all(middle_list)

                db.commit()
                # db.flush()
                db.refresh(db_update)
                return db_update
            except Exception as e:
                db.rollback()
                logger.debug(e)
            finally:
                db.close()
        else:
            return None


    def get_user_roles(self, db: Session, users):
        roles_users_sets = db.query(UsersRoles).filter_by(userId=users.id).all()
        rolesIds = [item.rolesId for item in roles_users_sets]
        roles_pers_sets = db.query(RolesPermission).filter(RolesPermission.id.in_(rolesIds)).all()
        persIds = [item.permissionId for item in roles_pers_sets]
        pers_sets = db.query(Permissions).filter(Permissions.id.in_(persIds)).all()
        data = [item.key for item in pers_sets]
        return data


user = CRUDUser(Users)
