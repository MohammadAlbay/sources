# -*- coding: utf-8 -*-

from datetime import datetime

con = MySqlConnection('server=localhost;user=root;database=db_test;port=3333;password=Mqlprovider_0')

def LogError(func,exp):
    print('W [File:search_for_suppliers, Func: '+func+'] ScriptError > '+str(exp)+'\n')


def IsValidSession(session):
    try:
        state = True
        r = None
        commandString = "select expd,uid,ip from sessions where sid='"+session+"';"
        cmd = MySqlCommand(commandString,con)
        rdr = cmd.ExecuteReader();
        if not rdr.Read():
            rdr.Close()
            state = False
            r = 1
        else:
            if rdr[0] == None or rdr[1] == None or rdr[2] == None:
                state = False
                r = 5
            else:
                uid = int(rdr[1])
                ip = rdr[2]
                
                if not (ip == ClientAddress.split(':')[0]):
                    state = False
                    r = 4
                else:
                    dNow = datetime.now()
                    expd = datetime.strptime(str(rdr[0]), '%d-%m-%Y %H:%M')

                    if dNow > expd:
                        state = False
                        r = 3
                    else:
                        state = True
                        r = uid
            rdr.Close()
        return [state, r]
    except Exception as exp:
        r += str(exp)
        LogError('IsValidSession', exp)
        return [False,  -1]

def BuildCommand(column, value, move, min, max, limit):
    if column == None and value == None and move == None:
        return 'SELECT * FROM suppliers LIMIT '+limit+';'
    if not move == ">" and not move == "<" :
        print('W [File:search_for_suppliers, Func: BuildCommand] ScriptError > invalid value assigned to "move". using base query as a fallback \n')
        return 'SELECT * FROM suppliers LIMIT '+limit+';'  
    if min == 0 and move == '>':
        move = '>='
    print(type(min))
    commandString = ''
    if column == None and value == None and min == 0:
        commandString = 'SELECT * FROM suppliers LIMIT '+limit+';'
    else:
        commandString = 'SELECT * FROM suppliers WHERE id '+move+' '+minID+' and '+column+' LIKE "%' + value + '%" LIMIT 2;'
# > forware
# < backward

def Search(column, value, move, min, max, limit):
    try:
        cmd = MySqlCommand(BuildCommand(column, value, move, min, max, limit),con)
        rdr = cmd.ExecuteReader()
        extra = '[' 
        count = 0
        firstFetchedID = 0
        lastFetchedID = 0
        while rdr.Read():
            if count == 0:
                firstFetchedID = rdr[0]
            count += 1
            debts = rdr[7]
            if str(rdr[7]) == "":
                debts = '[]'
            lastFetchedID = rdr[0]
            extra += '{"id": '+str(rdr[0])+',"fullname":"'+rdr[1]+'", "phone": "'+rdr[2]+'", "resident": "'+rdr[3]+'", "work": "'+rdr[4]+'", "position": '+str(rdr[5])+', "date": "'+rdr[6]+'", "debts": '+debts+'},'

        rdr.Close()
        # GET MAX, MIN VALUES OF id
        commandString = "select min(id), max(id) from suppliers;"
        cmd = MySqlCommand(commandString,con)
        rdr = cmd.ExecuteReader()
        if rdr.Read():
            canMoveForward = "false"
            if not (rdr[1] == lastFetchedID):
                canMoveForward = "true"

            canMoveBackword = "true"
            if (rdr[0] == firstFetchedID):
                canMoveBackword = "false"
            extra += '{"can-move-forward": '+canMoveForward+', "max-id":'+str(rdr[1])+', "can-move-backword": '+canMoveBackword+', "min-id": '+str(rdr[0])+'},'
        rdr.Close()
        if not count == 0:
            extra = extra[:-1] 
        extra += ']' 
        
        return [True, 0, extra]
    except Exception as exp:
        LogError('Search', exp)
        return [False, -1]


def GetSuppliersCount():
    try:
        commandString = 'select count(id) from suppliers;'
        cmd = MySqlCommand(commandString,con)
        rdr = cmd.ExecuteReader()
        if not rdr.Read():
            rdr.Close()
            return [False, 5]
        else:
            rdr.Close()
            return [True, 0, 6]
    except Exception as exp:
        LogError('GetSuppliersCount', exp)
        return [False, -1]


def HandleRequest():
    #
    # fetch count
    #
    if ServerParams.HasKey('fetch_count'):
        result = GetSuppliersCount()
        if not result[0]:
            ServerResult = '{"state":0, "code": '+str(result[1]) +', "extra": ""}' 
        else:
            ServerResult = '{"state":1, "code": '+str(result[1]) +', "extra": '+str(result[2])+'}' 
    #
    # fetch count
    #
    elif ServerParams.HasKey('initial'):
        pass
    #
    # fetch count
    #
    elif ServerParams.HasKey('search'):
        pass
    #
    # fetch count
    #
    elif ServerParams.HasKey('move'):
        pass



try:
    con.Open()
    result = IsValidSession(ServerParams.Get('sid').strip())
    if not result[0]:
        ServerResult = '{"state":0, "code": '+str(result[1]) +', "extra": ""}' 
    else:
        HandleRequest()
except Exception as exp:
    con.Close()
    LogError("___main___", exp)
    ServerResult = '{"state":0, "code": -1, "extra": ""}' 
finally:
    con.Close()







"""
if ServerParams.HasKey('fetch_count'):
            result = GetSuppliersCount()
            if not result[0]:
                ServerResult = '{"state":0, "code": '+str(result[1]) +', "extra": ""}' 
            else:
                ServerResult = '{"state":1, "code": '+str(result[1]) +', "extra": '+str(result[2])+'}' 
        else:
            if not ServerParams.HasKey('move') or not ServerParams.HasKey('limit'):
                ServerResult = '{"state":0, "code": 2, "extra": ""}'
            else:
                limit = int(ServerParams.Get('limit'))
                if ServerParams.HasKey('initial'):
                    result = Search(None, None, None, 0, 0, str(limit))
                else:
                    move = ServerParams.Get('move').strip()
                    if move == '0': # search
                        result = Search(
                            ServerParams.Get('type').strip(),
                            ServerParams.Get('value').strip(),
                            '>', 0, 0
                        )
                    elif move == '-1': # backward
                        pass
                    elif move == '1': # forward
                        pass

                if not result[0]:
                    ServerResult = '{"state":0, "code": '+str(result[1]) +', "extra": ""}' 
                else:
                    ServerResult = '{"state":1, "code": '+str(result[1]) +', "extra": '+result[2]+'}' 
"""