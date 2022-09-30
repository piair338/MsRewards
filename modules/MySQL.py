import mysql.connector


def add_row(compte, points, mycursor, mydb):
    sql = "INSERT INTO daily (compte, points, date) VALUES (%s, %s, current_date())"
    val = (compte, points)
    mycursor.execute(sql, val)
    mydb.commit()
    #printf(mycursor.rowcount, "record created.")


def update_row(compte, points, mycursor, mydb):
    sql = f"UPDATE daily SET points = {points} WHERE compte = '{compte}' AND date = current_date() ;"
    mycursor.execute(sql)
    mydb.commit()
    #printf(mycursor.rowcount, "record(s) updated")


def update_last(compte, points, mycursor, mydb):
    sql = f"UPDATE comptes SET last_pts = {points} WHERE compte = '{compte}';"
    mycursor.execute(sql)
    mydb.commit()
    #printf(mycursor.rowcount, "record(s) updated")


def get_row(compte, points, mycursor, same_points = True): #return if there is a line with the same ammount of point or with the same name as well as the same day
    if same_points :
        mycursor.execute(f"SELECT * FROM daily WHERE points = {points} AND compte = '{compte}' AND date = current_date() ;")
    else :
        mycursor.execute(f"SELECT * FROM daily WHERE compte = '{compte}' AND date = current_date() ;")
    myresult = mycursor.fetchall()
    return(len(myresult) == 1)


def add_to_database(compte, points, sql_host,sql_usr,sql_pwd,sql_database ):
    mydb = mysql.connector.connect(
        host=sql_host,
        user=sql_usr,
        password=sql_pwd,
        database = sql_database
    )
    mycursor = mydb.cursor()

    if get_row(compte, points,mycursor, True): #check if the row exist with the same ammount of points and do nothind if it does
        #printf("les points sont deja bon")
        return(0)
    elif get_row(compte, points,mycursor, False) : #check if the row exist, but without the same ammount of points and update the point account then
        update_row(compte, points,mycursor,mydb)
        #printf("row updated")
        return(1)
    else : # if the row don't exist, create it with the good ammount of points
        add_row(compte, points,mycursor,mydb)
        return(2) #printf("row added")
    if int(points) > 10 :
        update_last(compte, points, mycursor, mydb)

    mycursor.close()
    mydb.close()


