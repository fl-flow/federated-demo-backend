from loguru import logger
from sqlalchemy import desc, and_
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from dashboard.app.models.user import UsersRecords
from dashboard.app.resources import strings as base

class CRUDRecords(object):
    def __init__(self):
        pass

    def get_(self, db: Session, userId: int):
        return db.query(UsersRecords).filter(UsersRecords.userId == userId).all()


    def get_filter(self, db: Session, *, query_info= {}, ids=None):
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
        query_ = None
        if query_info:
            if 'and' in query_info:
                #将筛选条件为空的去除
                query_info['and'] = {item: query_info['and'][item] for item in query_info['and'] if query_info['and'][item]}
                query_curd = [getattr(UsersRecords, item) == query_info['and'][item] for item in query_info['and']
                              if query_info['and'][item] if getattr(UsersRecords, item, None)]
                if 'time_range' in query_info and query_info['time_range']:
                    query_info['time_range']['create_et'] += " 23:59:59"
                    query_ = db.query(UsersRecords).filter(and_(*query_curd)).filter(and_(UsersRecords.createTime >= query_info['time_range']['create_st'],
                                                                                  UsersRecords.createTime <= query_info['time_range']['create_et']))
                else:
                    query_ = db.query(UsersRecords).filter(and_(*query_curd))
            else:
                query_ = db.query(UsersRecords)
            if ids:
                query_ = query_.filter(UsersRecords.id.in_(ids))
            querys_count = len(query_.all())
            if query_info['page'] and query_info['page_size']:
                start = (int(query_info['page']) - 1) * int(query_info['page_size'])
                if query_info['order_by']:
                    if '-' in query_info['order_by']:
                        key = (query_info['order_by'].split('-'))[1]
                        per_tuple_list = query_.order_by(desc(key)).limit(int(query_info['page_size'])).offset(start).all()
                    else:
                        per_tuple_list = query_.order_by(query_info['order_by']).limit(int(query_info['page_size'])).offset(start).all()
                else:
                    per_tuple_list = query_.limit(int(query_info['page_size'])).offset(start).all()
                results = {"list": [v.to_dict() for v in per_tuple_list]}
                return results, querys_count
        else:
            querys = db.query(UsersRecords)
            if ids:
                query_ = db.query(UsersRecords).filter(UsersRecords.id.in_(ids))
            querys_count = querys.count()
            results = {"like": [v.to_dict() for v in querys.all()]}
            return results, querys_count

    #根据用户操作表获取historyLoginOrgCode
    def get_history_orgcode(self, db: Session, userId: int):
        usersrecords = db.query(UsersRecords).filter(UsersRecords.userId==userId,
                                                     UsersRecords.module==base.MODULES['login'], UsersRecords.orgCode != '')\
                                                     .order_by(UsersRecords.createTime.desc()).first()
        if not usersrecords:
            return None
        orgCode = usersrecords.orgCode
        if orgCode:
            return orgCode
        return None

    #记录登录信息
    def create_records(self, db: Session, info: {}):
        if not isinstance(info, dict):
            obj_in_data = jsonable_encoder(info)
        else:
            obj_in_data = info
        try:
            db_obj = UsersRecords(**obj_in_data)  # type: ignore
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            print(e)
            logger.debug("用户{} {}".format(info["userId"],e))
            db_obj = None
        return db_obj

    #获取用户操作信息
    def operation_create(self, db: Session, user_id: int, module: str, request, orgcode=None, return_code=None, remark=None):
        user = crud.user.get(db=db, id=int(user_id))
        phoneNumber = user.phoneNumber
        userName = user.realName
        method = request.method
        if module not in list(base.MODULES.keys()):
            return None
        module = base.MODULES[module]
        route = str(request.url).split('?')[0].split('/')[3:]
        api = '/' + ('/').join(route)
        info = {"userId": int(user_id), "userName": userName, "phoneNumber": phoneNumber, "path": api,
                "methodType": method, "module": module, "orgCode": orgcode, "returnResult": return_code, "remark": remark}
        data = self.create_records(db=db, info=info)
        return data




crud_records = CRUDRecords()


