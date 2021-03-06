# -*- coding: utf-8 -*-
"""
Created on 2017/3/19

@author: will4906
"""
import time

import copy

from entity.QueryTarget import QueryTarget


class SearchNameDefine:
    INVENTION_TYPE = '发明类型'
    REQUEST_NUMBER = '申请号'
    REQUEST_DATE = '申请日'
    PUBLISH_NUMBER = '公开（公告）号'
    PUBLISH_DATE = '公开（公告）日'
    PROPOSER_NAME = '申请（专利权）人'
    INVENTOR_NAME = '发明人'
    PRIORITY_NUMBER = '优先权号'
    PRIORITY_DATE = '优先权日'
    ABSTRACT = '摘要'
    CLAIM = '权利要求'
    INSTRUCTIONS = '说明书'
    KEY_WORD = '关键词'
    PUBLISH_COUNTRY = '公开国'


# 日期选择器
class DateSelect:
    def __init__(self, select='=', date='2001-01-01', enddate=None):
        # 符号：'=', '>', '>=', '<', '<=', ':'
        self.select = select
        # 日期（固定格式）,eg: 2001-01-01
        self.date = date
        # 结束日期，当符号位为":"时，此变量有效，只从date开始到enddate结束
        self.enddate = enddate

    def __repr__(self):
        return 'DateSelect{select=' + str(self.select) + ',date=' + str(self.date) + ',enddate=' + str(self.enddate)

    def __str__(self):
        return 'DateSelect{select=' + str(self.select) + ',date=' + str(self.date) + ',enddate=' + str(self.enddate)


class QueryItem:
    def __init__(self, requestNumber=None, requestDate=None, publishNumber=None, publishDate=None, proposerName=None,
                 inventorName=None, priorityNumber=None, priorityDate=None, abstract=None, claim=None,
                 instructions=None, keyword=None, inventionType=None, publishCountry=None):
        # 申请号
        self.requestNumber = requestNumber
        # 申请日
        self.requestDate = requestDate
        # 公开（公告）号
        self.publishNumber = publishNumber
        # 公开（公告）日
        self.publishDate = publishDate
        # 申请（专利权）人
        self.proposerName = proposerName
        # 发明人
        self.inventorName = inventorName
        # 优先权号
        self.priorityNumber = priorityNumber
        # 优先权日
        self.priorityDate = priorityDate
        # 摘要
        self.abstract = abstract
        # 权利要求
        self.claim = claim
        # 说明书
        self.instructions = instructions
        # 关键词
        self.keyword = keyword
        # 发明类型
        self.inventionType = inventionType
        # 公开国
        self.publishCountry = publishCountry

        self.targetList = []

        self.searchExpList = []

        self.define = {
            SearchNameDefine.REQUEST_NUMBER: 'requestNumber',
            SearchNameDefine.REQUEST_DATE: 'requestDate',
            SearchNameDefine.PUBLISH_NUMBER: 'publishNumber',
            SearchNameDefine.PUBLISH_DATE: 'publishDate',
            SearchNameDefine.PROPOSER_NAME: 'proposerName',
            SearchNameDefine.INVENTOR_NAME: 'inventorName',
            SearchNameDefine.PRIORITY_NUMBER: 'priorityNumber',
            SearchNameDefine.PRIORITY_DATE: 'priorityDate',
            SearchNameDefine.ABSTRACT: 'abstract',
            SearchNameDefine.CLAIM: 'claim',
            SearchNameDefine.INSTRUCTIONS: 'instructions',
            SearchNameDefine.KEY_WORD: 'keyword',
            SearchNameDefine.INVENTION_TYPE: 'inventionType',
            # SearchNameDefine.PUBLISH_COUNTRY: 'publishCountry'
        }

    '''
        以下代码均为生成表达式代码，用户均不需关心
    '''
    # 妈的，下面这段有点恶心
    def generateSearchExp(self):
        AND = " AND "
        typeDict = {}
        for (define, propertyName) in self.define.items():
            resultList = self.__generateElementExp(self.__getattribute__(propertyName), define)
            if resultList is None:
                continue
            else:
                typeDict[propertyName] = resultList
        lastSearchList = []
        for (propertyName, resultList) in typeDict.items():
            lastlen = len(lastSearchList)
            resultListLen = len(resultList)
            temp = []
            temp.extend(lastSearchList)
            for r in range(1, resultListLen):
                for last in lastSearchList:
                    temp.append(last)
            lastSearchList = []
            for result in resultList:
                if lastlen == 0:
                    lastSearchList.append(result)
                for index, item in enumerate(temp):
                    lastSearchList.append(item + result)
                    if index == lastlen - 1:
                        break
        for last in lastSearchList:
            self.searchExpList.append(last[:last.rindex(AND)])

    # 生成一个元素的表达式或表达式组
    def __generateElementExp(self, target, targetDefine):
        if target is None:
            return
        if isinstance(target, list):
            tarExpList = []
            for tar in target:
                if targetDefine == SearchNameDefine.REQUEST_NUMBER or targetDefine == SearchNameDefine.PUBLISH_NUMBER:
                    tarExpList.append(self.__generageNumberExp(tar, targetDefine))
                elif targetDefine == SearchNameDefine.REQUEST_DATE or targetDefine == SearchNameDefine.PUBLISH_DATE or targetDefine == SearchNameDefine.PRIORITY_DATE:
                    tarExpList.append(self.__generateDateExp(tar, targetDefine))
                else:
                    tarExpList.append(self.__generageNormalExp(tar, targetDefine))
            return tarExpList
        else:
            if targetDefine == SearchNameDefine.REQUEST_NUMBER or targetDefine == SearchNameDefine.PUBLISH_NUMBER:
                tarExp = self.__generageNumberExp(target, targetDefine)
            elif targetDefine == SearchNameDefine.REQUEST_DATE or targetDefine == SearchNameDefine.PUBLISH_DATE or targetDefine == SearchNameDefine.PRIORITY_DATE:
                tarExp = self.__generateDateExp(target, targetDefine)
            else:
                tarExp = self.__generageNormalExp(target, targetDefine)
            return [tarExp]

    # 生成日期型的表达式
    def __generateDateExp(self, target, targetDefine):
        AND = " AND "
        if isinstance(target, DateSelect):
            if target.select != ':':
                searchExp = targetDefine + target.select + target.date + AND
            else:
                searchExp = targetDefine + target.date + target.select + target.enddate + AND
            return searchExp
        else:
            return None

    # 生成普通型表达式
    def __generageNormalExp(self, target, targetDefine):
        AND = " AND "
        searchExp = targetDefine + "=(" + target + ")" + AND
        return searchExp

    # 申请号和公告号表达式
    def __generageNumberExp(self, target, targetDefine):
        AND = " AND "
        if target[0:2] == 'ZL':
            target = 'CN' + target[2:]
        if targetDefine == SearchNameDefine.REQUEST_NUMBER:
            target = target.split('.')[0]
        if target[0:2].isalpha() is False:
            target = '+' + target
        if target[len(target) - 1:] != '+':
            searchExp = targetDefine + "=(" + target + "+)" + AND
        else:
            searchExp = targetDefine + "=(" + target + ")" + AND
        return searchExp

    # 生成目标
    def createTarget(self):
        typeDict = {}
        for (define, propertyName) in self.define.items():
            resultList = self.__getattribute__(propertyName)
            if resultList is None:
                continue
            else:
                if isinstance(resultList, list) is False:
                    resultList = [resultList]
                typeDict[propertyName] = resultList
        targetCache = []
        for (propertyName, resultList) in typeDict.items():
            tempCache = []
            for result in resultList:
                tarLen = len(targetCache)
                if tarLen == 0:
                    qt = QueryTarget()
                    qt.__setattr__(propertyName, result)
                    targetCache.append(copy.deepcopy(qt))
                else:
                    for tarC in targetCache:
                        tarC.__setattr__(propertyName, result)
                        tempCache.append(copy.deepcopy(tarC))
            if len(tempCache) > 0:
                targetCache = copy.deepcopy(tempCache)
        self.targetList = targetCache




















