' Module: Sheet1.cls
' Stream: _VBA_PROJECT_CUR/VBA/Sheet1
' Source: C:\Users\rando\repos\reAA\경주대종천하류보20250501.xls
' ============================================================

Attribute VB_Name = "Sheet1"
Attribute VB_Base = "0{00020820-0000-0000-C000-000000000046}"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Attribute VB_TemplateDerived = False
Attribute VB_Customizable = True
Attribute VB_Control = "CB_dir_start, 13, 0, MSForms, ComboBox"
Attribute VB_Control = "CB_dir_end, 14, 1, MSForms, ComboBox"
Attribute VB_Control = "CB_mNum, 15, 2, MSForms, ComboBox"
Private Sub CB_dir_end_Change()

If CB_dir_end = "LEW" Then

    CB_dir_start = "REW"

ElseIf CB_dir_end = "REW" Then

    CB_dir_start = "LEW"

End If


End Sub

Private Sub CB_dir_start_Change()

If CB_dir_start = "LEW" Then

    CB_dir_end = "REW"

ElseIf CB_dir_start = "REW" Then

    CB_dir_end = "LEW"

End If

End Sub

Private Sub CB_mNum_Click()
    Select Case Worksheets("이름정의").Range("D11")
        Case "M1"
            i = 1
            Worksheets("입력시트").CB_dir_start = Worksheets("입력저장1").Range("C8").Offset(0, 0)
            'Worksheets("입력시트").CB_dir_end = Worksheets("입력저장1").Range("C8").Offset(101, 0)
            Do While Worksheets("입력저장1").Range("C8").Offset(i, 0) <> ""
                Worksheets("입력시트").Range("C8:s8").Offset(i, 0).ClearContents
                Worksheets("입력시트").Range("C8:s8").Offset(i, 0) = Worksheets("입력저장1").Range("C8:s8").Offset(i, 0).Value
                i = i + 1
            Loop
        Case "M2"
            i = 1
            Worksheets("입력시트").CB_dir_start = Worksheets("입력저장2").Range("C8").Offset(0, 0)
            'Worksheets("입력시트").CB_dir_end = Worksheets("입력저장2").Range("C8").Offset(101, 0)
            Do While Worksheets("입력저장2").Range("C8").Offset(i, 0) <> ""
                Worksheets("입력시트").Range("C8:s8").Offset(i, 0).ClearContents
                Worksheets("입력시트").Range("C8:s8").Offset(i, 0) = Worksheets("입력저장2").Range("C8:s8").Offset(i, 0).Value
                i = i + 1
            Loop
    End Select
End Sub

