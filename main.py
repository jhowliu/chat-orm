#!/usr/bin/env python
# -*- coding=utf-8 -*-
from schema import *
from engine import sess

# QUERY STATEMENT
class RobotHandler():
    def __init__(self, venderId):
        self._venderId = venderId
        self._sess = sess

    def list_robots(self):
        rows = sess.query(Robots).all()
        return map(lambda row: row.__dict__, rows)

    def robot_info(self):
        row = sess.query(Robots).filter(Robots.VenderId==self._venderId).one()
        return row.__dict__

    def get_greeting_msg(self):
        row = sess.query(Robots.GreetingMsg) \
                  .filter(Robots.VenderId==self._venderId).one()
        if row.GreetingMsg:
            return row.GreetingMsg.splitlines()
        else:
            return ["你好，請問需要什麼服務？"]

    def get_failed_msg(self):
        row = sess.query(Robots.FailedMsg) \
                  .filter(Robots.VenderId==self._venderId).one()
        if row.FailedMsg:
            return row.FailedMsg.splitlines()
        else:
            return ["抱歉，這個問題超出我的理解範圍"]

    def get_histories(self, deviceId=None):
        """
        Fetch the histories for certain deviceId(line/facebook userid)

        @return [dict]
        """
        q = sess.query(Histories)

        if deviceId:
            print("UFC")
            q = q.filter(Histories.DeviceId==deviceId)
        else:
            q = q.join(Robots) \
                 .filter(Robots.VenderId==self._venderId)

        rows = q.order_by(Histories.CreateAt) \
                .limit(50)

        return map(lambda row: row.__dict__, rows)

    def save_histories(self, histories):

        return


if __name__ == '__main__':
    handler = RobotHandler('HVC');

    print('\n===LIST ROBOTS===\n')
    rows = handler.list_robots()
    print(rows)

    print('\n===LIST ROBOT INFO===\n')
    row = handler.robot_info()
    print(row)

    print('\n===LIST GREETING MSG===\n')
    print(handler.get_greeting_msg())

    print('\n===LIST HISTORIES===\n')
    print(handler.get_histories())
