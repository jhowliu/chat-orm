#!/usr/bin/env python
# -*- coding=utf-8 -*-
from schema import Robots
from engine import sess

# QUERY STATEMENT
result = sess.query(Robots.RobotName, \
                    Robots.Platform, \
                    Robots.VenderId).one()
print(','.join(result))

# INSERT STATEMENT add_all(list of class) or add
