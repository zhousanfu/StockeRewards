# coding=utf-8
'''
Author: sanford courageux_san@wechat.com
Date: 2024-11-23 05:44:01
LastEditors: sanford courageux_san@wechat.com
LastEditTime: 2025-01-05 16:33:07
FilePath: /script/StockeRewards/util/db.py
Description: 
'''
import os
import requests
import json
import sqlite3
import datetime


CLOUDFLARE_D1_APK_KEY = os.getenv("CLOUDFLARE_D1_APK_KEY")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_DATABASE_ID = os.getenv("CLOUDFLARE_DATABASE_ID")
CURRENT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = CURRENT_DIRECTORY+'/db/stocke_rewards.db'
DB_SQL_PATH = CURRENT_DIRECTORY+'/db/stocke_rewards.sql'


class CloudflareD1Client:
    def __init__(self, account_id, api_token, database_id):
        self.account_id = account_id
        self.api_token = api_token
        self.database_id = database_id
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        if not self._table_exists():
            self._create_tables()

    def execute_query(self, query, params=None):
        endpoint = f"{self.base_url}/raw"
        payload = {
            "sql": query,
            "params": params or []
        }
        response = requests.post(endpoint, headers=self.headers, json=payload)
        print(response.json())
        return response.json()
    
    def _table_exists(self, table_name: str="stocke_rewards") -> bool:
        """检查指定表是否存在"""
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        self.cursor.execute(query, (table_name,))
        return self.cursor.fetchone() is not None

    def _create_tables(self):
        """打开SQL文件并逐条执行SQL语句"""
        with open(DB_SQL_PATH, 'r') as file:
            sql_script = file.read()
        
        sql_statements = sql_script.split(';')
        for statement in sql_statements:
            statement = statement.strip()
            if statement:
                self.execute_query(statement)

    def query_data(self, table_name: str, condition: dict = None):
        """
        从指定表中查询数据
        :param table_name: 表名
        :param condition: 查询条件字典
        """
        query = f"SELECT * FROM {table_name}"
        params = []

        if condition:
            conditions = []
            for field, value in condition.items():
                if value is None:
                    conditions.append(f"{field} IS NULL")
                elif isinstance(value, tuple):
                    operator, val = value
                    conditions.append(f"{field} {operator} ?")
                    params.append(val)
                else:
                    conditions.append(f"{field} = ?")
                    params.append(value)
            query += " WHERE " + " AND ".join(conditions)

        return self.execute_query(query, params)

    def insert_data(self, table_name: str, data: dict):
        """
        向指定表中插入数据
        :param table_name: 表名
        :param data: 要插入的数据字典
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        return self.execute_query(query, list(data.values()))

    def update_data(self, table_name: str, data: dict, condition: dict):
        """
        更新指定表中的数据
        :param table_name: 表名
        :param data: 要更新的数据字典
        :param condition: 更新条件字典
        """
        set_clause = ', '.join(f"{field} = ?" for field in data.keys())
        conditions = ' AND '.join(f"{field} = ?" for field in condition.keys())
        query = f"UPDATE {table_name} SET {set_clause} WHERE {conditions}"
        params = list(data.values()) + list(condition.values())
        return self.execute_query(query, params)

    def delete_data(self, table_name: str, condition: dict):
        """
        从指定表中删除数据
        :param table_name: 表名
        :param condition: 删除条件字典
        """
        conditions = ' AND '.join(f"{field} = ?" for field in condition.keys())
        query = f"DELETE FROM {table_name} WHERE {conditions}"
        return self.execute_query(query, list(condition.values()))

class DB:
    def __init__(self, create_tables: bool=False):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("PRAGMA timezone = '+08:00'")
        self.cursor = self.conn.cursor()
        self.conn.create_function('beijing_time', 0, lambda: datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S'))
        if not self._table_exists():
            self._create_tables()

    def _table_exists(self, table_name: str="stocke_rewards") -> bool:
        """检查指定表是否存在"""
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        self.cursor.execute(query, (table_name,))
        return self.cursor.fetchone() is not None

    def _create_tables(self):
        """打开SQL文件并逐条执行SQL语句"""
        with open(DB_SQL_PATH, 'r') as file:
            sql_script = file.read()
        
        sql_statements = sql_script.split(';')
        for statement in sql_statements:
            statement = statement.strip()
            if statement:
                self.cursor.execute(statement)
        self.conn.commit()

    def get_db_data(self, table_name: str):
        self.cursor.execute("SELECT * FROM {table_name}")
        data = self.cursor.fetchall()

        return data

    def query_data(self, table_name: str, condition: dict = None):
        """
        从指定表中查询数据并返回 JSON 格式
        :param table_name: 表名
        :param condition: 查询条件字典，支持以下格式：
            - {'field': value} 表示相等
            - {'field': None} 表示为空
            - {'field': (operator, value)} 表示其他比较操作，如 {'latency': ('<=', 1000)}
        """
        query = f"SELECT * FROM {table_name}"
        params = []
        results = []

        if condition:
            conditions = []
            for field, value in condition.items():
                if value is None:  # 添加对 None 值的处理
                    conditions.append(f"{field} IS NULL")
                elif isinstance(value, tuple):
                    operator, val = value
                    conditions.append(f"{field} {operator} ?")
                    params.append(val)
                else:
                    conditions.append(f"{field} = ?")
                    params.append(value)
            query += " WHERE " + " AND ".join(conditions)

        with self.conn:
            self.cursor.execute(query, params)
            columns = [description[0] for description in self.cursor.description]
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))
        
        return results

    def insert_data(self, table_name: str, data: dict):
        """
        向指定表中插入数据
        :param table_name: 表名
        :param data: 要插入的数据字典
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        with self.conn:
            self.cursor.execute(query, tuple(data.values()))

    def update_data(self, table_name: str, data: dict, condition: dict):
        """
        更新指定表中的数据
        :param table_name: 表名
        :param data: 要更新的数据字典 --{'score': 100}
        :param condition: 更新条件字典 -- {'id': 1}
        示例: db.update_data('stocke_rewards', {'score': 100}, {'id': 1})
        """
        set_clause = ', '.join(f"{field} = ?" for field in data.keys())
        conditions = ' AND '.join(f"{field} = ?" for field in condition.keys())
        query = f"UPDATE {table_name} SET {set_clause} WHERE {conditions}"
        with self.conn:
            self.cursor.execute(query, tuple(data.values()) + tuple(condition.values()))

    def delete_data(self, table_name: str, condition: dict):
        """
        从指定表中删除数据
        :param table_name: 表名
        :param condition: 删除条件字典
        """
        conditions = ' AND '.join(f"{field} = ?" for field in condition.keys())
        query = f"DELETE FROM {table_name} WHERE {conditions}"
        with self.conn:
            self.cursor.execute(query, tuple(condition.values()))

    def close(self):
        """关闭数据库连接"""
        self.cursor.close()
        self.conn.close()




if __name__=="__main__":
    # db = DB()
    # res = db.query_data(table_name="stocke_rewards", condition={'has_reward': None})
    # print(res[:3])
    # db.close()
    print(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S'))


    d1_client = CloudflareD1Client(
        account_id=CLOUDFLARE_ACCOUNT_ID,
        api_token=CLOUDFLARE_D1_APK_KEY,
        database_id=CLOUDFLARE_DATABASE_ID
        )
    # 查询数据
    result = d1_client.query_data("users", {"status": "active"})
    # 插入数据
    d1_client.insert_data("users", {"name": "张三", "email": "zhangsan@example.com"})