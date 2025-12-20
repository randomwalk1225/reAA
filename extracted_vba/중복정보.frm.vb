' Module: 중복정보.frm
' Stream: _VBA_PROJECT_CUR/VBA/중복정보
' Source: C:\Users\rando\repos\reAA\경주대종천하류보20250501.xls
' ============================================================

Attribute VB_Name = "중복정보"
Attribute VB_Base = "0{14FADD50-C1EA-4051-8000-7EB0B5898EA5}{38C38608-5ABD-4A66-8FE1-3D01A04698A2}"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Attribute VB_TemplateDerived = False
Attribute VB_Customizable = False
Private Sub cmbselect_Click()
    
    j = CmbSelect.ListIndex + 1
    기본입력.T하천명 = Matrix(j, 2)
    기본입력.TDM = Matrix(j, 1)
    중복정보.Hide

End Sub


Private Sub CmbSelect_Change()

End Sub

Private Sub UserForm_Activate()

    중복정보.CmbSelect.Clear
    중복정보.CmbSelect.Text = "중복된 관측소명이 있습니다. 지점을 선택하세요"
                       
    For k = 1 To i
        중복정보.CmbSelect.AddItem (기본입력.T지점명.Text & "-" & Left(Matrix(k, 1), 7) & "-" & Matrix(k, 2))
    Next

End Sub



