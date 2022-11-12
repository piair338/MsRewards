#add return a string witx tabs
def tabs(x):
    return(x*4*" ")


#create dictionnary with all progress bars
def dico(progress):
    dico_task = {
        "daily" : {
            "all" : progress.add_task("[yellow]daily", total=100, start=False, visible=False),
            "carte1" : progress.add_task(f"[yellow]{tabs(1)}carte 1", total=100, start=False, visible = False),
            "carte2" : progress.add_task(f"[yellow]{tabs(1)}carte 2", total=100, start=False, visible = False),
            "carte3" : progress.add_task(f"[yellow]{tabs(1)}carte 3", total=100, start=False, visible = False)
        },
        "weekly" : {
            "all" : progress.add_task("[yellow]weekly", total=100, start=False, visible=False),
            "carte1" : progress.add_task(f"[yellow]{tabs(1)}carte 1", total=100, start=False, visible = False),
            "carte2" : progress.add_task(f"[yellow]{tabs(1)}carte 2", total=100, start=False, visible = False),
            "carte3" : progress.add_task(f"[yellow]{tabs(1)}carte 3", total=100, start=False, visible = False),
            "carte3" : progress.add_task(f"[yellow]{tabs(1)}carte 4", total=100, start=False, visible = False),
            "carte3" : progress.add_task(f"[yellow]{tabs(1)}carte 5", total=100, start=False, visible = False),
            "carte3" : progress.add_task(f"[yellow]{tabs(1)}carte 6", total=100, start=False, visible = False),
            "carte3" : progress.add_task(f"[yellow]{tabs(1)}carte 7", total=100, start=False, visible = False),
            "carte3" : progress.add_task(f"[yellow]{tabs(1)}carte 8", total=100, start=False, visible = False),
            "carte3" : progress.add_task(f"[yellow]{tabs(1)}carte 9", total=100, start=False, visible = False),
        },
        "PC" : progress.add_task(f"[yellow]PC", total=100, start=False, visible = False),
        "Mobile" : progress.add_task(f"[yellow]Mobile", total=100, start=False, visible = False),


    }
    return(dico_task)