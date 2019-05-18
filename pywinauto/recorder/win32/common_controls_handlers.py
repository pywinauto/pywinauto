from ... import win32defines
from ...win32_element_info import HwndElementInfo
from ...controls.hwndwrapper import HwndWrapper
from win32api import LOWORD, HIWORD

_B_NOTIFICATIONS = {
    win32defines.BCN_DROPDOWN      : "BCN_DROPDOWN",
    win32defines.BCN_HOTITEMCHANGE : "BCN_HOTITEMCHANGE",
    win32defines.BN_DBLCLK         : "BN_DBLCLK",
    win32defines.BN_PUSHED         : "BN_PUSHED",
    win32defines.BN_UNPUSHED       : "BN_UNPUSHED",
    win32defines.BN_CLICKED        : "BN_CLICKED",
    win32defines.BN_DISABLE        : "BN_DISABLE",
    win32defines.BN_DOUBLECLICKED  : "BN_DOUBLECLICKED",
    win32defines.BN_HILITE         : "BN_HILITE",
    win32defines.BN_KILLFOCUS      : "BN_KILLFOCUS",
    win32defines.BN_PAINT          : "BN_PAINT",
    win32defines.BN_SETFOCUS       : "BN_SETFOCUS",
    win32defines.BN_UNHILITE       : "BN_UNHILITE",
}

_E_NOTIFICATIONS = {
    win32defines.EN_CHANGE    : "EN_CHANGE",
    win32defines.EN_ERRSPACE  : "EN_ERRSPACE",
    win32defines.EN_HSCROLL   : "EN_HSCROLL",
    win32defines.EN_KILLFOCUS : "EN_KILLFOCUS",
    win32defines.EN_MAXTEXT   : "EN_MAXTEXT",
    win32defines.EN_SETFOCUS  : "EN_SETFOCUS",
    win32defines.EN_UPDATE    : "EN_UPDATE",
    win32defines.EN_VSCROLL   : "EN_VSCROLL",
}

_CB_NOTIFICATIONS = {
    win32defines.CBN_CLOSEUP      : "CBN_CLOSEUP",
    win32defines.CBN_DBLCLK       : "CBN_DBLCLK",
    win32defines.CBN_DROPDOWN     : "CBN_DROPDOWN",
    win32defines.CBN_EDITCHANGE   : "CBN_EDITCHANGE",
    win32defines.CBN_EDITUPDATE   : "CBN_EDITUPDATE",
    win32defines.CBN_ERRSPACE     : "CBN_ERRSPACE",
    win32defines.CBN_KILLFOCUS    : "CBN_KILLFOCUS",
    win32defines.CBN_SELCHANGE    : "CBN_SELCHANGE",
    win32defines.CBN_SELENDCANCEL : "CBN_SELENDCANCEL",
    win32defines.CBN_SELENDOK     : "CBN_SELENDOK",
    win32defines.CBN_SETFOCUS     : "CBN_SETFOCUS",
}

_LV_NOTIFICATIONS = {
    win32defines.LVN_BEGINLABELEDITA : "LVN_BEGINLABELEDIT",
    win32defines.LVN_BEGINLABELEDITW : "LVN_BEGINLABELEDIT",
    win32defines.LVN_COLUMNDROPDOWN : "LVN_COLUMNDROPDOWN",
    win32defines.LVN_BEGINSCROLL : "LVN_BEGINSCROLL",
    win32defines.LVN_COLUMNOVERFLOWCLICK : "LVN_COLUMNOVERFLOWCLICK",
    win32defines.LVN_ENDLABELEDIT : "LVN_ENDLABELEDIT",
    win32defines.LVN_ENDSCROLL : "LVN_ENDSCROLL",
    win32defines.LVN_GETDISPINFO : "LVN_GETDISPINFO",
    win32defines.LVN_GETEMPTYMARKUP : "LVN_GETEMPTYMARKUP",
    win32defines.LVN_GETINFOTIP : "LVN_GETINFOTIP",
    win32defines.LVN_INCREMENTALSEARCH : "LVN_INCREMENTALSEARCH",
    win32defines.LVN_LINKCLICK : "LVN_LINKCLICK",
    win32defines.LVN_SETDISPINFO : "LVN_SETDISPINFO",
    win32defines.LVN_ODFINDITEM : "LVN_ODFINDITEM",
    win32defines.LVN_BEGINDRAG : "LVN_BEGINDRAG",
    win32defines.LVN_BEGINRDRAG : "LVN_BEGINRDRAG",
    win32defines.LVN_COLUMNCLICK : "LVN_COLUMNCLICK",
    win32defines.LVN_DELETEALLITEMS : "LVN_DELETEALLITEMS",
    win32defines.LVN_DELETEITEM : "LVN_DELETEITEM",
    win32defines.LVN_HOTTRACK : "LVN_HOTTRACK",
    win32defines.LVN_INSERTITEM : "LVN_INSERTITEM",
    win32defines.LVN_ITEMACTIVATE : "LVN_ITEMACTIVATE",
    win32defines.LVN_ITEMCHANGED : "LVN_ITEMCHANGED",
    win32defines.LVN_ITEMCHANGING : "LVN_ITEMCHANGING",
    win32defines.LVN_KEYDOWN : "LVN_KEYDOWN",
    win32defines.LVN_MARQUEEBEGIN : "LVN_MARQUEEBEGIN",
    win32defines.LVN_ODCACHEHINT : "LVN_ODCACHEHINT",
    win32defines.LVN_ODSTATECHANGED : "LVN_ODSTATECHANGED",
    win32defines.NM_CLICK : "NM_CLICK",
    win32defines.NM_DBLCLK : "NM_DBLCLK",
    win32defines.NM_HOVER : "NM_HOVER",
    win32defines.NM_KILLFOCUS : "NM_KILLFOCUS",
    win32defines.NM_RCLICK : "NM_RCLICK",
    win32defines.NM_RDBLCLK : "NM_RDBLCLK",
    win32defines.NM_RELEASEDCAPTURE : "NM_RELEASEDCAPTURE",
    win32defines.NM_RETURN : "NM_RETURN",
    win32defines.NM_SETFOCUS : "NM_SETFOCUS",
}

_LB_NOTIFICATIONS = {
    win32defines.LBN_DBLCLK     : "LBN_DBLCLK",
    win32defines.LBN_ERRSPACE   : "LBN_ERRSPACE",
    win32defines.LBN_KILLFOCUS  : "LBN_KILLFOCUS",
    win32defines.LBN_SELCANCEL  : "LBN_SELCANCEL",
    win32defines.LBN_SELCHANGE  : "LBN_SELCHANGE",
    win32defines.LBN_SETFOCUS   : "LBN_SETFOCUS",
}

_TV_NOTIFICATIONS = {
    win32defines.NM_CLICK : "NM_CLICK",
    win32defines.NM_DBLCLK : "NM_DBLCLK",
    win32defines.NM_KILLFOCUS : "NM_KILLFOCUS",
    win32defines.NM_RCLICK : "NM_RCLICK",
    win32defines.NM_RDBLCLK : "NM_RDBLCLK",
    win32defines.NM_RETURN : "NM_RETURN",
    win32defines.NM_SETCURSOR : "NM_SETCURSOR",
    win32defines.NM_SETFOCUS : "NM_SETFOCUS",
    win32defines.TVN_ASYNCDRAW : "TVN_ASYNCDRAW",
    win32defines.TVN_BEGINDRAGA : "TVN_BEGINDRAG",
    win32defines.TVN_BEGINDRAGW : "TVN_BEGINDRAG",
    win32defines.TVN_BEGINLABELEDITA : "TVN_BEGINLABELEDIT",
    win32defines.TVN_BEGINLABELEDITW : "TVN_BEGINLABELEDIT",
    win32defines.TVN_BEGINRDRAGA : "TVN_BEGINRDRAG",
    win32defines.TVN_DELETEITEMA : "TVN_DELETEITEM",
    win32defines.TVN_ENDLABELEDITA : "TVN_ENDLABELEDIT",
    win32defines.TVN_GETDISPINFOA : "TVN_GETDISPINFO",
    win32defines.TVN_GETINFOTIPA : "TVN_GETINFOTIP",
    win32defines.TVN_ITEMEXPANDINGA : "TVN_ITEMEXPANDING",
    win32defines.TVN_SELCHANGEDA : "TVN_SELCHANGED",
    win32defines.TVN_SELCHANGINGA : "TVN_SELCHANGING",
    win32defines.TVN_SETDISPINFOA : "TVN_SETDISPINFO",
    win32defines.TVN_ITEMEXPANDEDA : "TVN_ITEMEXPANDED",
    win32defines.TVN_BEGINRDRAGW : "TVN_BEGINRDRAG",
    win32defines.TVN_DELETEITEMW : "TVN_DELETEITEM",
    win32defines.TVN_ENDLABELEDITW : "TVN_ENDLABELEDIT",
    win32defines.TVN_GETDISPINFOW : "TVN_GETDISPINFO",
    win32defines.TVN_GETINFOTIPW : "TVN_GETINFOTIP",
    win32defines.TVN_ITEMEXPANDINGW : "TVN_ITEMEXPANDING",
    win32defines.TVN_SELCHANGEDW : "TVN_SELCHANGED",
    win32defines.TVN_SELCHANGINGW : "TVN_SELCHANGING",
    win32defines.TVN_SETDISPINFOW : "TVN_SETDISPINFO",
    win32defines.TVN_ITEMEXPANDEDW : "TVN_ITEMEXPANDED",
    win32defines.TVN_ITEMCHANGED : "TVN_ITEMCHANGED",
    win32defines.TVN_ITEMCHANGING : "TVN_ITEMCHANGING",
    win32defines.TVN_KEYDOWN : "TVN_KEYDOWN",
    win32defines.TVN_SINGLEEXPAND : "TVN_SINGLEEXPAND",
}

_CBE_NOTIFICATIONS = {
    win32defines.CBEN_DRAGBEGIN : "CBEN_DRAGBEGIN",
    win32defines.CBEN_ENDEDIT : "CBEN_ENDEDIT",
    win32defines.CBEN_GETDISPINFO : "CBEN_GETDISPINFO",
    win32defines.CBEN_BEGINEDIT : "CBEN_BEGINEDIT",
    win32defines.CBEN_DELETEITEM : "CBEN_DELETEITEM",
    win32defines.CBEN_INSERTITEM : "CBEN_INSERTITEM",
    win32defines.NM_SETCURSOR : "NM_SETCURSOR",
}

_DT_NOTIFICATIONS = {
    win32defines.DTN_FORMAT : "DTN_FORMAT",
    win32defines.DTN_FORMATQUERY : "DTN_FORMATQUERY",
    win32defines.DTN_USERSTRING : "DTN_USERSTRING",
    win32defines.DTN_WMKEYDOWN : "DTN_WMKEYDOWN",
    win32defines.DTN_CLOSEUP : "DTN_CLOSEUP",
    win32defines.DTN_DATETIMECHANGE : "DTN_DATETIMECHANGE",
    win32defines.DTN_DROPDOWN : "DTN_DROPDOWN",
    win32defines.NM_KILLFOCUS : "NM_KILLFOCUS",
    win32defines.NM_SETFOCUS : "NM_SETFOCUS",
}

_HD_NOTIFICATIONS = {
    win32defines.HDN_BEGINTRACKA : "HDN_BEGINTRACK",
    win32defines.HDN_DIVIDERDBLCLICKA : "HDN_DIVIDERDBLCLICK",
    win32defines.HDN_ENDTRACKA : "HDN_ENDTRACK",
    win32defines.HDN_GETDISPINFOA : "HDN_GETDISPINFO",
    win32defines.HDN_ITEMCHANGINGA : "HDN_ITEMCHANGING",
    win32defines.HDN_ITEMCLICKA : "HDN_ITEMCLICK",
    win32defines.HDN_ITEMDBLCLICKA : "HDN_ITEMDBLCLICK",
    win32defines.HDN_TRACKA : "HDN_TRACK",
    win32defines.HDN_BEGINFILTEREDIT : "HDN_BEGINFILTEREDIT",
    win32defines.HDN_BEGINTRACKW : "HDN_BEGINTRACK",
    win32defines.HDN_DIVIDERDBLCLICKW : "HDN_DIVIDERDBLCLICK",
    win32defines.HDN_ENDTRACKW : "HDN_ENDTRACK",
    win32defines.HDN_GETDISPINFOW : "HDN_GETDISPINFO",
    win32defines.HDN_ITEMCHANGINGW : "HDN_ITEMCHANGING",
    win32defines.HDN_ITEMCLICKW : "HDN_ITEMCLICK",
    win32defines.HDN_ITEMDBLCLICKW : "HDN_ITEMDBLCLICK",
    win32defines.HDN_TRACKW : "HDN_TRACK",
    win32defines.HDN_DROPDOWN : "HDN_DROPDOWN",
    win32defines.HDN_ENDFILTEREDIT : "HDN_ENDFILTEREDIT",
    win32defines.HDN_FILTERBTNCLICK : "HDN_FILTERBTNCLICK",
    win32defines.HDN_FILTERCHANGE : "HDN_FILTERCHANGE",
    win32defines.HDN_ITEMCHANGED : "HDN_ITEMCHANGED",
    win32defines.HDN_ITEMKEYDOWN : "HDN_ITEMKEYDOWN",
    win32defines.HDN_ITEMSTATEICONCLICK : "HDN_ITEMSTATEICONCLICK",
    win32defines.HDN_OVERFLOWCLICK : "HDN_OVERFLOWCLICK",
    win32defines.HDN_BEGINDRAG : "HDN_BEGINDRAG",
    win32defines.HDN_ENDDRAG : "HDN_ENDDRAG",
    win32defines.NM_RCLICK : "NM_RCLICK",
    win32defines.NM_RELEASEDCAPTURE : "NM_RELEASEDCAPTURE",
}

_IP_NOTIFICATIONS = {
    win32defines.IPN_FIELDCHANGED : "IPN_FIELDCHANGED",
}

_MC_NOTIFICATIONS = {
    win32defines.MCN_VIEWCHANGE : "MCN_VIEWCHANGE",
    win32defines.MCN_GETDAYSTATE : "MCN_GETDAYSTATE",
    win32defines.MCN_SELCHANGE : "MCN_SELCHANGE",
    win32defines.MCN_SELECT : "MCN_SELECT",
    win32defines.NM_RELEASEDCAPTURE : "NM_RELEASEDCAPTURE",
}

_PG_NOTIFICATIONS = {
    win32defines.PGN_HOTITEMCHANGE : "PGN_HOTITEMCHANGE",
    win32defines.NM_RELEASEDCAPTURE : "NM_RELEASEDCAPTURE",
    win32defines.PGN_CALCSIZE : "PGN_CALCSIZE",
    win32defines.PGN_SCROLL : "PGN_SCROLL",
}

_RB_NOTIFICATIONS = {
    win32defines.NM_NCHITTEST : "NM_NCHITTEST",
    win32defines.NM_RELEASEDCAPTURE : "NM_RELEASEDCAPTURE",
    win32defines.RBN_AUTOSIZE : "RBN_AUTOSIZE",
    win32defines.RBN_BEGINDRAG : "RBN_BEGINDRAG",
    win32defines.RBN_CHILDSIZE : "RBN_CHILDSIZE",
    win32defines.RBN_DELETEDBAND : "RBN_DELETEDBAND",
    win32defines.RBN_DELETINGBAND : "RBN_DELETINGBAND",
    win32defines.RBN_ENDDRAG : "RBN_ENDDRAG",
    win32defines.RBN_GETOBJECT : "RBN_GETOBJECT",
    win32defines.RBN_HEIGHTCHANGE : "RBN_HEIGHTCHANGE",
    win32defines.RBN_LAYOUTCHANGED : "RBN_LAYOUTCHANGED",
    win32defines.RBN_AUTOBREAK : "RBN_AUTOBREAK",
    win32defines.RBN_CHEVRONPUSHED : "RBN_CHEVRONPUSHED",
    win32defines.RBN_MINMAX : "RBN_MINMAX",
    win32defines.RBN_SPLITTERDRAG : "RBN_SPLITTERDRAG",
}

_ST_NOTIFICATIONS = {
    win32defines.STN_CLICKED : "STN_CLICKED",
    win32defines.STN_DBLCLK : "STN_DBLCLK",
    win32defines.STN_DISABLE : "STN_DISABLE",
    win32defines.STN_ENABLE : "STN_ENABLE",
}

_SB_NOTIFICATIONS = {
    win32defines.NM_CLICK : "NM_CLICK",
    win32defines.NM_DBLCLK : "NM_DBLCLK",
    win32defines.NM_RCLICK : "NM_RCLICK",
    win32defines.NM_RDBLCLK : "NM_RDBLCLK",
    win32defines.SBN_SIMPLEMODECHANGE : "SBN_SIMPLEMODECHANGE",
}

_TC_NOTIFICATIONS = {
    win32defines.TCN_FOCUSCHANGE : "TCN_FOCUSCHANGE",
    win32defines.NM_CLICK : "NM_CLICK",
    win32defines.NM_DBLCLK : "NM_DBLCLK",
    win32defines.NM_RCLICK : "NM_RCLICK",
    win32defines.NM_RDBLCLK : "NM_RDBLCLK",
    win32defines.NM_RELEASEDCAPTURE : "NM_RELEASEDCAPTURE",
    win32defines.TCN_GETOBJECT : "TCN_GETOBJECT",
    win32defines.TCN_KEYDOWN : "TCN_KEYDOWN",
    win32defines.TCN_SELCHANGE : "TCN_SELCHANGE",
    win32defines.TCN_SELCHANGING : "TCN_SELCHANGING",
}

_TB_NOTIFICATIONS = {
    win32defines.NM_CHAR : "NM_CHAR",
    win32defines.NM_CLICK : "NM_CLICK",
    win32defines.NM_DBLCLK : "NM_DBLCLK",
    win32defines.NM_KEYDOWN : "NM_KEYDOWN",
    win32defines.NM_LDOWN : "NM_LDOWN",
    win32defines.NM_RCLICK : "NM_RCLICK",
    win32defines.NM_RDBLCLK : "NM_RDBLCLK",
    win32defines.NM_RELEASEDCAPTURE : "NM_RELEASEDCAPTURE",
    win32defines.TBN_BEGINADJUST : "TBN_BEGINADJUST",
    win32defines.TBN_BEGINDRAG : "TBN_BEGINDRAG",
    win32defines.TBN_CUSTHELP : "TBN_CUSTHELP",
    win32defines.TBN_DELETINGBUTTON : "TBN_DELETINGBUTTON",
    win32defines.TBN_DRAGOUT : "TBN_DRAGOUT",
    win32defines.TBN_DROPDOWN : "TBN_DROPDOWN",
    win32defines.TBN_ENDADJUST : "TBN_ENDADJUST",
    win32defines.TBN_ENDDRAG : "TBN_ENDDRAG",
    win32defines.TBN_GETOBJECT : "TBN_GETOBJECT",
    win32defines.TBN_HOTITEMCHANGE : "TBN_HOTITEMCHANGE",
    win32defines.TBN_QUERYDELETE : "TBN_QUERYDELETE",
    win32defines.TBN_QUERYINSERT : "TBN_QUERYINSERT",
    win32defines.TBN_TOOLBARCHANGE : "TBN_TOOLBARCHANGE",
    win32defines.TBN_RESET : "TBN_RESET",
    win32defines.TBN_INITCUSTOMIZE : "TBN_INITCUSTOMIZE",
    win32defines.TBN_MAPACCELERATOR : "TBN_MAPACCELERATOR",
    win32defines.TBN_DUPACCELERATOR : "TBN_DUPACCELERATOR",
    win32defines.TBN_DRAGOVER : "TBN_DRAGOVER",
    win32defines.TBN_GETINFOTIPA : "TBN_GETINFOTIP",
    win32defines.TBN_GETBUTTONINFOA : "TBN_GETBUTTONINFO",
    win32defines.TBN_GETDISPINFOA : "TBN_GETDISPINFO",
    win32defines.TBN_GETINFOTIPW : "TBN_GETINFOTIP",
    win32defines.TBN_GETBUTTONINFOW : "TBN_GETBUTTONINFO",
    win32defines.TBN_GETDISPINFOW : "TBN_GETDISPINFO",
    win32defines.TBN_RESTORE : "TBN_RESTORE",
    win32defines.TBN_SAVE : "TBN_SAVE",
    win32defines.NM_TOOLTIPSCREATED : "NM_TOOLTIPSCREATED",
    win32defines.TBN_WRAPACCELERATOR : "TBN_WRAPACCELERATOR",
    win32defines.TBN_WRAPHOTITEM : "TBN_WRAPHOTITEM",
}

_TT_NOTIFICATIONS = {
    win32defines.TTN_GETDISPINFOA : "TTN_GETDISPINFO",
    win32defines.TTN_GETDISPINFOW : "TTN_GETDISPINFO",
    win32defines.TTN_NEEDTEXTW : "TTN_NEEDTEXT",
    win32defines.TTN_LINKCLICK : "TTN_LINKCLICK",
    win32defines.TTN_POP : "TTN_POP",
    win32defines.TTN_SHOW : "TTN_SHOW",
}

_TRB_NOTIFICATIONS = {
    win32defines.NM_RELEASEDCAPTURE : "NM_RELEASEDCAPTURE",
    win32defines.TRBN_THUMBPOSCHANGING : "TRBN_THUMBPOSCHANGING",
}

_UD_NOTIFICATIONS = {
    win32defines.NM_RELEASEDCAPTURE : "NM_RELEASEDCAPTURE",
    win32defines.UDN_DELTAPOS : "UDN_DELTAPOS",
}

_AC_NOTIFICATIONS = {
    win32defines.ACN_START : "ACN_START",
    win32defines.ACN_STOP : "ACN_STOP",
}

_CLASS_NAME_TO_NOTIFICATIONS = {
    "ComboBoxEx"     : _CBE_NOTIFICATIONS,
    "Trackbar"       : _TRB_NOTIFICATIONS,
    "ComboBox"       : _CB_NOTIFICATIONS,
    "ListView"       : _LV_NOTIFICATIONS,
    "TreeView"       : _TV_NOTIFICATIONS,
    "ListBox"        : _LB_NOTIFICATIONS,
    "DateTimePicker" : _DT_NOTIFICATIONS,
    "Header"         : _HD_NOTIFICATIONS,
    "IPAddress"      : _IP_NOTIFICATIONS,
    "Calendar"       : _MC_NOTIFICATIONS,
    "Pager"          : _PG_NOTIFICATIONS,
    "ReBar"          : _RB_NOTIFICATIONS,
    "Static"         : _ST_NOTIFICATIONS,
    "StatusBar"      : _SB_NOTIFICATIONS,
    "TabControl"     : _TC_NOTIFICATIONS,
    "Toolbar"        : _TB_NOTIFICATIONS,
    "ToolTips"       : _TT_NOTIFICATIONS,
    "UpDown"         : _UD_NOTIFICATIONS,
    "Animation"      : _AC_NOTIFICATIONS,
    "Edit"           : _E_NOTIFICATIONS,
    "Button"         : _B_NOTIFICATIONS,
    "PropertySheet"  : {}, # shold be added to common_controls
    "RichEdit"       : {},
    "Scroll"         : {},
    "SysLink"        : {},
    "TaskDialog"     : {},
}

def resolve_handle_to_event(element, msg, is_command):
    class_name = HwndWrapper(element).friendlyclassname
    print(class_name)
    if element and class_name in _CLASS_NAME_TO_NOTIFICATIONS:
        message_list = _CLASS_NAME_TO_NOTIFICATIONS[class_name]
        if is_command and HIWORD(msg.wParam) in message_list:
            return message_list[HIWORD(msg.wParam)]
        if not is_command and msg.lParam in message_list:
            return message_list[msg.lParam]
    elif element:
        print("[WARNING] Unhandled class_name = " + element.class_name)


