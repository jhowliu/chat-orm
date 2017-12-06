#!/usr/bin/env python
# -*- coding=utf-8 -*-
import datetime

from schema import *
from engine import sess

from sqlalchemy.sql import func

# QUERY STATEMENT
class RobotHandler():
    def __init__(self, venderId):
        self._venderId = venderId
        self._sess = sess

    def get_robot_list(self):
        rows = sess.query(Robots).all()
        return map(lambda row: row.__dict__, rows)

    def get_robot_info(self):
        row = sess.query(Robots).filter(Robots.VenderId == self._venderId).one()
        return row.__dict__

    def get_greeting_msg(self):
        row = sess.query(Robots.GreetingMsg) \
                  .filter(Robots.VenderId == self._venderId).one()
        if row.GreetingMsg:
            return row.GreetingMsg.splitlines()
        else:
            return ["你好，請問需要什麼服務？"]

    def get_failed_msg(self):
        row = sess.query(Robots.FailedMsg) \
                  .filter(Robots.VenderId == self._venderId).one()
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
            q = q.filter(Histories.DeviceId == deviceId)
        else:
            q = q.join(Robots) \
                 .filter(Robots.VenderId == self._venderId)

        rows = q.order_by(Histories.CreateAt) \
                .limit(50)

        return map(lambda row: row.__dict__, rows)

    def get_qa_list(self):
        """
        Fetch all pair of question and answer

        @ return {
            group_id: {
                question,
                answer
            },
            group_id: {
                question,
                answer
            }...
        }
        """
        results = {}
        rows = sess.query(Groups.GroupId, Questions.Content, Answers.Content) \
                   .join(Robots) \
                   .filter(Robots.VenderId == self._venderId) \
                   .filter(Groups.GroupId  == Questions.GroupId) \
                   .filter(Groups.GroupId  == Answers.GroupId) \
                   .all()

        for row in rows:
            (group_id, question, ans) = row
            results[row.GroupId] = {
                "Question": question,
                "Answer"  : ans
            }

        return results

    def get_user_count(self, ndays=7):
        """
        Fetch statistic in the ndays

        @return {
            date: {
                user_count,
                question_count
            },
            date: {
                user_count,
                question_count
            }...
        }
        """
        results = {}
        start_t = datetime.datetime.now()
        start_t -= datetime.timedelta(days=ndays)

        rows = sess.query(func.date(Histories.CreateAt), \
                        func.count(func.distinct(Histories.DeviceId)), \
                        func.count(Histories.id)) \
                   .filter(Histories.CreateAt >= func.date(start_t)) \
                   .group_by(func.date(Histories.CreateAt)) \
                   .all()

        for row in rows:
            (date, user_cnt, q_cnt) = row
            results[date] = {
                "question_count": q_cnt,
                "user_count": user_cnt
            }

        return results

    def save_qa(self, qas):
        """
        Save the Q&A

        @param {
            group_id: {
                question
                answer
            }...
        }

        @return {
            success: true
        }
        """


if __name__ == '__main__':
    handler = RobotHandler('HVC');

    print('\n===LIST ROBOTS===\n')
    rows = handler.get_robot_list()
    print(rows)

    print('\n===LIST ROBOT INFO===\n')
    row = handler.get_robot_info()
    print(row)

    print('\n===LIST GREETING MSG===\n')
    print(handler.get_greeting_msg())

    print('\n===LIST HISTORIES===\n')
    print(handler.get_histories())

    print(handler.get_qa_list())

    print(handler.get_user_count())
