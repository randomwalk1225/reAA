' Module: ufSelCal.frm
' Stream: _VBA_PROJECT_CUR/VBA/ufSelCal
' Source: C:\Users\rando\repos\reAA\경주대종천하류보20250501.xls
' ============================================================

Attribute VB_Name = "ufSelCal"
Attribute VB_Base = "0{FACF0A5E-78D2-4A7F-83C4-1BA5D69EB744}{CD8189A5-1846-4269-B692-7326D2A9FB65}"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Attribute VB_TemplateDerived = False
Attribute VB_Customizable = False
Private Sub cbCancel_Click()
    Unload Me
    End '2013.12.05 이기성 수정
End Sub
Private Sub cbOKCal_Click()
   '****************************************************************************************
   ' 1번 측정한 경우 그것이 1차이든 2차 측정값이든 상관없이 저장, 계산등의 수행시
   ' "입력저장1" 및 "계산1" 과 같이 1번시트에 기록됨
   '****************************************************************************************
    ufSelCal.Hide '완성후 삭제
    If (ufSelCal.cbSelect1.Value = False And ufSelCal.cbSelect2.Value = True) Then   '2번측정
        Call calFlow(1)
        Call calFlow(2)
    ElseIf (ufSelCal.cbSelect1.Value = True And ufSelCal.cbSelect2.Value = False) Then  '1번측정
        Call calFlow(1)
    End If
    
    Unload Me
End Sub
