# -*- coding: utf-8 -*- 

import wx
import wx.adv
import time
import hashlib
import numpy
import matplotlib as mpl
import wx.grid
import pandas as pd
#use WXagg as backend, embed the matplotlib into wxpython
mpl.use("WXAgg")
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar

class PlotNotebook(wx.Panel):
    def __init__(self, parent, id=-1, dpi=None, **kwargs):
        wx.Panel.__init__(self, parent, id=id, **kwargs)
        self.figure = mpl.figure.Figure(dpi=dpi, figsize=(4, 10))
        self.canvas = FigureCanvas(self, 1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        self.ax1 = self.figure.add_subplot(1,2,1)
        self.ax2 = self.figure.add_subplot(1,2,2)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolbar, 1, wx.LEFT | wx.EXPAND, 5)
        sizer.Add(self.canvas, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)
        self.Fit()

    def draw_image(self, y, labels):
        self.ax1.clear()
        self.ax2.clear()
        self.figure.set_canvas(self.canvas)
        self.ax1.pie(y, labels = labels, labeldistance=0.3,autopct='%1.1f%%')
        x = numpy.arange(len(y))
        self.ax2.bar(x, y, tick_label=labels, alpha=0.5, width=0.4)
        self.canvas.draw()
    
    def savefig(self, *args, **kwargs):
        self.figure.savefig(*args, **kwargs)


class TaskPanel(wx.Panel):
    def __init__(self, parent, id, tags, owner):
        wx.Panel.__init__(self, parent, id)
        self.tags = tags
        self.tag_name = None
        self.bSizer_upper = wx.BoxSizer( wx.HORIZONTAL )
        self.m_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.On_m_timer, self.m_timer)
        self.counter = 0
        self.add_tag_radiobox()
        self.add_time_box()
        self.owner = owner
        self.add_Task_Box()
        self.SetSizer(self.bSizer_upper)
        self.Layout()
        self.bSizer_upper.Fit(self)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        
    def add_tag_radiobox(self):
        self.tag_radiobox = wx.RadioBox(self, wx.ID_ANY, label="Tag",
            choices=self.tags, majorDimension=3, style=wx.RA_SPECIFY_COLS)
        self.bSizer_upper.Add(self.tag_radiobox, 0, wx.ALL, 0)
        
    def get_the_selected_tag(self):
        index = self.tag_radiobox.GetSelection()
        if index != "NOT_FOUND":
            self.tag_name = self.tag_radiobox.GetString(index)
            return self.tag_name
        return False

    def add_time_box(self):
        #Create the Time region
        TimeBox = wx.StaticBoxSizer( wx.StaticBox(self, wx.ID_ANY, u"Timer" ), wx.VERTICAL)
        bSizer_time = wx.BoxSizer( wx.HORIZONTAL )
        StartTimeButton = wx.BitmapButton( TimeBox.GetStaticBox(), wx.ID_ANY, 
            wx.Bitmap( u"start_48.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW)
        bSizer_time.Add( StartTimeButton, 0, wx.ALL, 0)
        StartTimeButton.Bind( wx.EVT_BUTTON, self.start_timer)

        ContinueTimeButton = wx.BitmapButton( TimeBox.GetStaticBox(), wx.ID_ANY, 
            wx.Bitmap( u"continue_48.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
        bSizer_time.Add( ContinueTimeButton, 0, wx.ALL, 0)
        ContinueTimeButton.Bind( wx.EVT_BUTTON, self.continue_timer)
        
        StopTimeButton = wx.BitmapButton( TimeBox.GetStaticBox(), wx.ID_ANY, 
            wx.Bitmap( u"stop_48.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
        bSizer_time.Add( StopTimeButton, 0, wx.ALL, 0)
        StopTimeButton.Bind( wx.EVT_BUTTON, self.stop_timer )
        TimeBox.Add( bSizer_time, 0, wx.EXPAND, 0)
        
        gSizer_time = wx.GridSizer( 0, 2, 0, 0 )
        
        gSizer_total_time = wx.GridSizer( 0, 2, 0, 0 )
        TotalTimeText = wx.StaticText( TimeBox.GetStaticBox(), wx.ID_ANY, "Used Time", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer_total_time.Add( TotalTimeText, 0, wx.ALL, 0 )
        self.TotalTimetextCtrl = wx.TextCtrl( TimeBox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer_total_time.Add(self.TotalTimetextCtrl, 0, wx.ALL|wx.EXPAND, 0 )
        TimeBox.Add( gSizer_total_time, 0, wx.ALL|wx.EXPAND, 0)
        
        gSizer_date = wx.GridSizer( 0, 2, 0, 0 )
        DateText = wx.StaticText( TimeBox.GetStaticBox(), wx.ID_ANY, "Date", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer_date.Add( DateText, 0, wx.ALL, 0)
        self.datePicker = wx.adv.DatePickerCtrl( TimeBox.GetStaticBox(), wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, 
            wx.DefaultSize, wx.adv.DP_DROPDOWN)
        gSizer_date.Add( self.datePicker, 0, wx.ALL|wx.EXPAND, 0 )
        TimeBox.Add( gSizer_date, 0, wx.ALL|wx.EXPAND, 0)

        AddButton = wx.Button( TimeBox.GetStaticBox(), wx.ID_ANY, "Add One Task", wx.DefaultPosition, wx.DefaultSize, 0 )
        AddButton.Bind(wx.EVT_BUTTON, self.add_one_task)
        TimeBox.Add(AddButton, 1, wx.ALL|wx.EXPAND, 5)
        self.bSizer_upper.Add(TimeBox, 1, wx.EXPAND, 5)
    
    def On_m_timer(self, event):
        self.counter += 1
        self.TotalTimetextCtrl.SetValue("%s" % (self.counter*0.5))

    def start_timer(self, event):
        self.counter = 0
        self.m_timer.Start(500)

    def stop_timer(self, event):
        self.m_timer.Stop()

    def continue_timer(self, event):
        self.m_timer.Start(-1)

    def OnQuit(self, event):
        self.Destroy()

    def add_Task_Box(self):
        TaskSize = wx.StaticBoxSizer(wx.StaticBox( self, wx.ID_ANY, "Task" ), wx.VERTICAL)
        self.task_items = ["Doc_No", "Version", "Process", "Customer"]
        self.taskTextCtrl = {}
        for item in self.task_items:
            gSizer = wx.GridSizer( 0, 2, 0, 0 )
            itemText = wx.StaticText( TaskSize.GetStaticBox(), wx.ID_ANY, item, wx.DefaultPosition, wx.DefaultSize, 0 )
            gSizer.Add( itemText, 0, wx.ALL, 0 )
            self.taskTextCtrl[item] = wx.TextCtrl( TaskSize.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
            self.taskTextCtrl[item].SetMaxLength( 32 )
            gSizer.Add( self.taskTextCtrl[item], 1, wx.ALL|wx.EXPAND, 5)
            TaskSize.Add(gSizer, 0, wx.ALL|wx.EXPAND, 0)
        
        gSizer_1 = wx.GridSizer( 0, 2, 0, 0 )
        DescriptionText = wx.StaticText( TaskSize.GetStaticBox(), wx.ID_ANY, "Description", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer_1.Add(DescriptionText, 0, wx.ALL, 0)
        self.DescriptionTextCtrl = wx.TextCtrl( TaskSize.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, 
            wx.DefaultSize, wx.TE_LEFT|wx.TE_MULTILINE|wx.TE_RICH )
        gSizer_1.Add( self.DescriptionTextCtrl, 1, wx.ALL|wx.EXPAND, 5 )
        TaskSize.Add( gSizer_1, 1, wx.ALL|wx.EXPAND, 5 )
        
        self.bSizer_upper.Add( TaskSize, 1, wx.ALL|wx.ALL, 5 )
    
    def add_one_task(self, event):
        one_task = {}
        one_task["ID"]= create_unique_id()
        tag = self.get_the_selected_tag()
        if not tag:
            print("you must choose one tag!")
        one_task["tag"] = tag
        one_task["description"] = self.DescriptionTextCtrl.GetValue()
        for item in self.task_items:
            one_task[item] = self.taskTextCtrl[item].GetValue()
        one_task["owner"] = self.owner
        one_task["spend_time"] = self.TotalTimetextCtrl.GetValue()
        m_now = time.localtime(time.time())
        one_task["create_time"] = time.strftime("%Y-%m-%d %H:%M:%S", m_now)
        one_task["modify_time"] = time.strftime("%Y-%m-%d %H:%M:%S", m_now)
        task_day = self.datePicker.GetValue()
        one_task["task_day"] = task_day
        #one_task["month"] = m_now.tm_mon
        IN = open("log.name", "a+")
        for key, value in one_task.items():
            IN.write("%s->%s" % (key,value))
            IN.write("\n")
        IN.write("\n")
        IN.close()

def create_unique_id():
    m = hashlib.md5()
    m.update(bytes(str(time.clock()), encoding='utf-8'))
    return m.hexdigest()

class TaskTableData(wx.grid.GridTableBase):
        
    def __init__(self):
        wx.grid.GridTableBase.__init__(self)
        self.colLabels = ["Tag Name", "Spend Time", "Description", "Date",  "Customer", "ID"]
        self.table = [["" for i in range(7)] for j in range(16)]

    def GetNumberRows(self):
        return len(self.table) - 1
        
    def GetNumberCols(self):
        return len(self.table[0]) - 1
    
    def IsEmptyCell(self, row, col):
        """judge whether this value of a cell is empty"""
        try:
            if self.table[row][col] is "":
                return True
            return False
        except IndexError:
            print("the row value or col value is out of range")
            return False
    
    def GetValue(self, row, col):
        """return the value of a cell"""
        try:
            return self.table[row][col]
        except IndexError:
            print("the row value or col value is out of range")
            return ""
    
    def SetValue(self, row, col, value):
        """set the value of a cell"""
        self.table[row][col] = value
    
    def UpdateTable(self, table):
        self.table = table
    
    def GetColLabelValue(self, index):
        return self.colLabels[index]
        

class TaskGrid(wx.grid.Grid):
    def __init__(self, *args, **kwargs):
        wx.grid.Grid.__init__(self, *args, **kwargs)
        self.table = TaskTableData()
        self.SetTable(self.table, takeOwnership=True)
        self.SetColSize(0, 120)
        self.SetColSize(1, 120)
        self.SetColSize(2, 200)
        self.SetColSize(3, 120)
        self.SetColSize(4, 120)
        self.SetColSize(5, 120)
    
    def Update_Value(self, data):
        self.EnableEditing(True)
        for col in range(6):
            for row in range(len(data)):
                self.table.SetValue(row, col, data[row][col])
        self.ForceRefresh()
        self.EnableEditing(False)

class TimeMainFrame (wx.Frame):
    
    def __init__(self, parent, tags, owner):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Time Tracing and Management", 
            pos = wx.DefaultPosition, size = wx.Size( -1,-1 ))
        
        ##get the tasks from the database or file
        self.task_list = [{"a":1, "b":1}, {"a":1, "b":1}, {"a":1, "b":1}]
        self.owner = owner

        ## create the menu "File", "Summary" and "Help"
        MainMenuBar = wx.MenuBar()
        MenuFile = wx.Menu()
        SaveMenuItem = wx.MenuItem( MenuFile, wx.ID_ANY, u"Save"+ u"\t" + u"CTRL+S", 
            u"update the time database and output the statistical data", wx.ITEM_NORMAL )
        SaveMenuItem.SetBitmap(wx.Bitmap( u"save_16.png", wx.BITMAP_TYPE_ANY ) )
        MenuFile.Append( SaveMenuItem )
        
        MenuFile.AppendSeparator()
        
        ExitMenuItem = wx.MenuItem( MenuFile, wx.ID_ANY, u"Exit"+ u"\t" + u"CTRL+Q", 
            u"close the Time Tracing and Management", wx.ITEM_NORMAL )
        ExitMenuItem.SetBitmap( wx.Bitmap( u"exit.png", wx.BITMAP_TYPE_ANY ) )
        MenuFile.Append( ExitMenuItem )
        
        MainMenuBar.Append( MenuFile, u"File" ) 
        
        HelpMenu = wx.Menu()
        ManualmenuItem = wx.MenuItem( HelpMenu, wx.ID_ANY, u"Manual"+ u"\t" + u"CTRL+H", 
            u"open the manual", wx.ITEM_NORMAL )
        ManualmenuItem.SetBitmap( wx.Bitmap( u"help_16.png", wx.BITMAP_TYPE_ANY ) )
        HelpMenu.Append( ManualmenuItem )
        
        MainMenuBar.Append( HelpMenu, u"Help" ) 
        
        self.SetMenuBar( MainMenuBar )
        
        ## create the status bar
        self.statusBar = self.CreateStatusBar( 3, wx.RAISED_BORDER, wx.ID_ANY )
        welcome_words = "Welcome to use the time Tracing! %s" % self.owner
        self.statusBar.SetStatusText(welcome_words, 2)
        ## show the system time
        self.frame_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.show_time, self.frame_timer)
        self.frame_timer.Start(1000)

        ## create the main Sizer
        MainSizer = wx.BoxSizer( wx.VERTICAL )
        self.TaskPanel = TaskPanel(self, wx.ID_ANY, tags, self.owner)
        # self.TaskPanel.Hide()
        MainSizer.Add( self.TaskPanel, 0, wx.EXPAND, 0)
        
        downsizer = wx.BoxSizer( wx.HORIZONTAL )
        down_left_Sizer = wx.BoxSizer(wx.VERTICAL)

        self.pltpanel_pie = PlotNotebook(self)
        self.pltpanel_pie.draw_image([0.1,0.2,0.3,0.4,0.5], ["a", "b", "c", "d", "e"])
        down_left_Sizer.Add(self.pltpanel_pie, 1, wx.ALL|wx.EXPAND, 5)

        gSizer_left = wx.GridSizer( 0, 2, 0, 0 )
        self.FromText = wx.StaticText(self, wx.ID_ANY, u"From", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer_left.Add( self.FromText, 0, wx.ALL|wx.EXPAND, 0 )
        
        self.m_datePicker_from = wx.adv.DatePickerCtrl(self, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.adv.DP_DROPDOWN)
        gSizer_left.Add( self.m_datePicker_from, 0, wx.ALL|wx.EXPAND, 0 )
        
        self.ToText = wx.StaticText(self, wx.ID_ANY, u"To", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer_left.Add( self.ToText, 0, wx.ALL|wx.EXPAND, 0 )
        
        self.m_datePicker_to = wx.adv.DatePickerCtrl(self, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.adv.DP_DROPDOWN)
        gSizer_left.Add( self.m_datePicker_to, 0, wx.ALL|wx.EXPAND, 0 )
        
        down_left_Sizer.Add( gSizer_left, 0, wx.ALL|wx.EXPAND, 0 )
        
        self.SummaryButton = wx.Button(self, wx.ID_ANY, u"Review", wx.DefaultPosition, wx.DefaultSize, 0 )
        down_left_Sizer.Add( self.SummaryButton, 0, wx.ALL, 0 )
        
        downsizer.Add( down_left_Sizer, 1, wx.ALL|wx.EXPAND, 5 )
        
        DetailSize = wx.StaticBoxSizer( wx.StaticBox(self, wx.ID_ANY, u"Details" ), wx.VERTICAL )
        self.taskgrid = TaskGrid(DetailSize.GetStaticBox())

        DetailSize.Add( self.taskgrid, 1, wx.EXPAND |wx.ALL, 5 )
        
        bSizer_right = wx.BoxSizer( wx.HORIZONTAL )
        
        self.UpdateButton = wx.Button( DetailSize.GetStaticBox(), wx.ID_ANY, u"Update", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_right.Add( self.UpdateButton, 1, wx.ALL, 5)
        self.UpdateButton.Bind(wx.EVT_BUTTON, self.update_task_list)
        
        self.DeleteButton = wx.Button( DetailSize.GetStaticBox(), wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_right.Add( self.DeleteButton, 1, wx.ALL, 5 )
        self.DeleteButton.Bind(wx.EVT_BUTTON, self.delete_the_selected_task)
        
        DetailSize.Add( bSizer_right, 0, wx.EXPAND, 0 )
        downsizer.Add( DetailSize, 1, wx.ALL|wx.EXPAND, 5 )

        MainSizer.Add( downsizer, 1, wx.EXPAND |wx.ALL, 5 )
                
        self.SetSizer( MainSizer )
        self.Layout()
        MainSizer.Fit( self )
        
        self.Centre( wx.BOTH )
        
        # Connect Events
        self.Bind( wx.EVT_MENU, self.save_the_task_by_excel, id = SaveMenuItem.GetId() )
        self.Bind( wx.EVT_MENU, self.exit_application, id = ExitMenuItem.GetId() )
        self.Bind( wx.EVT_TOOL, self.open_manual, id = ManualmenuItem.GetId() )
        self.SummaryButton.Bind( wx.EVT_BUTTON, self.ShowStatisticalImage )
    
    def show_time(self, event):
        TimeString = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        self.statusBar.SetStatusText(TimeString, 1)

    def ShowStatisticalImage(self, event):
        from_date = self.m_datePicker_from.GetValue()
        to_date = self.m_datePicker_to.GetValue()
        self.pltpanel_pie.draw_image([0.1,0.2,0.3,0.4,2], ["a", "b", "c", "d", "e"])

    def update_task_list(self, event):
        data_test = [["Customer", "0.5h", "HVOD.R.2 for C651", "C651", "2019-07-20 11:40", "123"]
                ,["Customer", "0.5h", "HVOD.R.2 for C651", "C651", "2019-07-20 11:40", "124"]
                ,["Customer", "0.5h", "HVOD.R.2 for C651", "C651", "2019-07-20 11:40", "125"]]
        self.taskgrid.Update_Value(data_test)

    def delete_the_selected_task(self, event):
        selected_rows = self.taskgrid.GetSelectedRows()
        """Get the ID, delete the rows, and then update the table"""
    
    def open_manual( self, event ):
        help_dlg = wx.MessageDialog(self,"Time Tracing and Management\n"
                        "To analyse the working hours and improve the productivity\n",
                        "On-developing", wx.OK | wx.ICON_INFORMATION)
        help_dlg.ShowModal()
        help_dlg.Destroy()
    
    def save_the_task_by_excel(self, event):
        task_DF = pd.DataFrame(self.task_list)
        file_name = self.owner + "_working_time.xls"
        task_DF.to_excel(file_name)
        self.statusBar.SetStatusText("sucessfully save the file.", 0)
    
    def exit_application(self, event):
        wx.Exit()
    

if __name__ == "__main__":
    tag_list = ["Co-Work", "Coding", "Coding_Review", "Cross_Review", "Customer_Support", 
        "Discussion", "Innovation", "Management", "Meeting", "Others", "Out_Sourcing", 
        "PER_Project_Plan", "Pattern", "Presentation", "QC_Flow", "Rescouce_Estimation", 
        "Script", "Study", "Survery_Summary", "Training"]
    app = wx.App()
    owner = "hlguo"
    frame = TimeMainFrame(None,tag_list, owner)
    frame.Show()
    app.MainLoop()