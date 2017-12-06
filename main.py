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
        rows = self._sess.query(Robots).all()
        return map(lambda row: row.__dict__, rows)

    def get_robot_info(self):
        row = self._sess.query(Robots).filter(Robots.VenderId == self._venderId).one()
        return row.__dict__

    def get_greeting_msg(self):
        row = self._sess.query(Robots.GreetingMsg) \
                  .filter(Robots.VenderId == self._venderId).one()
        if row.GreetingMsg:
            return row.GreetingMsg.splitlines()
        else:
            return ["你好，請問需要什麼服務？"]

    def get_failed_msg(self):
        row = self._sess.query(Robots.FailedMsg) \
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
        q = self._sess.query(Histories)

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
        rows = self._sess.query(Groups.GroupId, Questions.Content, Answers.Content) \
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

        rows = self._sess.query(func.date(Histories.CreateAt), \
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

    def add_new_groups(self, create_time):
        """
        Create a new group from new Q&A

        @return group_id
        """
        robot = self.get_robot_info()

        group = Groups(
                    RobotId=robot['id'], \
                    CreateAt=create_time \
                )

        self._sess.add(group)
        self._sess.commit()

        row = self._sess.query(func.max(Groups.GroupId)) \
                        .first()

        return row[0]

    def add_qa(self, qa):
        """
        Save the Q&A

        @param qa = {
            question
            answer
        }

        @return {
            success: true
        }
        """
        create_time = datetime.datetime.now()
        group_id = self.add_new_groups(create_time)

        question = Questions(
                      GroupId=group_id, \
                      Content=qa['question'], \
                      CreateAt=create_time, \
                      UpdateAt=create_time \
                   )

        answer = Answers(
                    GroupId=group_id, \
                    Content=qa['answer'], \
                    CreateAt=create_time, \
                    UpdateAt=create_time \
                 )
        try:
            self._sess.add(question)
            self._sess.add(answer)
            self._sess.commit()
        except Exception as ex:
            return {
                'success': False,
                'msg': str(ex)
            }

        return { 'success': True }

    def add_qas(self, qas):
        """
        Add a list of Q&A

        @param qas=[
            {
                question
                answer
            },...
        ]
        """
        for qa in qas:
            self.add_qa(qa)

