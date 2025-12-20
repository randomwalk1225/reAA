' Module: 기본입력.frm
' Stream: _VBA_PROJECT_CUR/VBA/기본입력
' Source: C:\Users\rando\repos\reAA\경주대종천하류보20250501.xls
' ============================================================

Attribute VB_Name = "기본입력"
Attribute VB_Base = "0{A28D9C96-6BCA-48FC-A581-032A652F0017}{3E159588-36D0-4DBD-BA17-C233414B46DF}"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Attribute VB_TemplateDerived = False
Attribute VB_Customizable = False

Private Sub CheckBox1_Click()

Dim i, com

    If CheckBox1.Value = True Then
        
        For i = 1 To 4
        
            Me.Controls("ComboBox" & i).Visible = True
        
        Next i
                
        TextBox1.Visible = True
        CheckBox2.Visible = True
                        
        'Set labelbox = Me.Controls.Add("Forms.Label.1", "Label" & 22)
        
        Me.Controls("Label" & 22).Visible = True
        Me.Controls("Label" & 22) = "측선별 적용 유속계 입력방법" & Chr(10) & Chr(10) & "1,2,3,7 또는 1-3,7"
        Me.Controls("Label" & 22).Width = 118
        Me.Controls("Label" & 22).Height = 27
        Me.Controls("Label" & 22).Left = 150
        Me.Controls("Label" & 22).Top = 72
    Else
        
        For i = 1 To 4
        
            Me.Controls("ComboBox" & i).Visible = False
        
        Next i
        
        TextBox1.Visible = False
        CheckBox2.Value = False
        CheckBox2.Visible = False
        
        
        
        Me.Controls("Label" & 22).Visible = False
        
    End If

End Sub
Private Sub CheckBox2_Click()
    If CheckBox2.Value = True Then
        
        For i = 5 To 8
        
            Me.Controls("ComboBox" & i).Visible = True
        
        Next i
                
        TextBox2.Visible = True
        CheckBox3.Visible = True
        Me.Controls("Label" & 22).Top = 108
        
    Else
    
        For i = 5 To 8
        
            Me.Controls("ComboBox" & i).Visible = False
        
        Next i
                    
        TextBox2.Visible = False
        CheckBox3.Value = False
        CheckBox3.Visible = False
        Me.Controls("Label" & 22).Top = 72
                    
    End If
End Sub
Private Sub CheckBox3_Click()
    If CheckBox3.Value = True Then

        For i = 9 To 12
        
            Me.Controls("ComboBox" & i).Visible = True
        
        Next i
                
        TextBox3.Visible = True
        CheckBox4.Visible = True
                        
        기본입력.MultiPage1.Height = 190
        
        기본입력.Height = 280
        
        CM확인.Top = 233
        CM취소.Top = 233

        Me.Controls("Label" & 22).Top = 145
        
    Else
        For i = 9 To 12
        
            Me.Controls("ComboBox" & i).Visible = False
        
        Next i
        
        TextBox3.Visible = False
        CheckBox4.Value = False
        CheckBox4.Visible = False
        
        기본입력.MultiPage1.Height = 154
        
        기본입력.Height = 245
        
        CM확인.Top = 198
        CM취소.Top = 198
        
        Me.Controls("Label" & 22).Top = 108
        
    End If
End Sub
Private Sub CheckBox4_Click()
        
    If CheckBox4.Value = True Then
        
        For i = 13 To 16
        
            Me.Controls("ComboBox" & i).Visible = True
        
        Next i
                
        TextBox4.Visible = True
        
        기본입력.MultiPage1.Height = 225
        기본입력.Height = 316
        CM확인.Top = 270
        CM취소.Top = 270
        
        Me.Controls("Label" & 22).Top = 181
        
    Else
        For i = 13 To 16
        
            Me.Controls("ComboBox" & i).Visible = False
        
        Next i
           
        TextBox4.Visible = False
        
        기본입력.MultiPage1.Height = 190
        기본입력.Height = 280
        CM확인.Top = 233
        CM취소.Top = 233
        
        Me.Controls("Label" & 22).Top = 145
        
    End If

End Sub

Private Sub CM취소_Click()
    End 'Unload Me
End Sub

Private Sub CM확인_Click()

10
    
기본입력.Hide
    
    Dim n, i, j, k, tex
        
        
        
    If InStr(C종류.Text, "기기종류") <> 0 Then
    
        MsgBox (C종류.Text & "를 입력하세요.")
        
        기본입력.MultiPage1.Value = 1
        C종류.SetFocus
        기본입력.Show
        GoTo 10
         
    End If
    
    If InStr(C번호.Text, "기기번호") <> 0 Then
    
        MsgBox (C번호.Text & "를 입력하세요.")
        
        기본입력.MultiPage1.Value = 1
        C번호.SetFocus
        기본입력.Show
        GoTo 10
         
    End If
    
    If InStr(C방식.Text, "입력방식") <> 0 Then
    
        MsgBox (C방식.Text & "를 입력하세요.")
        
        기본입력.MultiPage1.Value = 1
        C방식.SetFocus
        기본입력.Show
        GoTo 10
         
    End If
    
    If InStr(C방법.Text, "측정방법") <> 0 Then
    
        MsgBox (C방법.Text & "를 입력하세요.")
        
        기본입력.MultiPage1.Value = 1
        C방법.SetFocus
        기본입력.Show
        GoTo 10
         
    End If
    
    For i = 1 To 16
        
        If i Mod 4 = 0 Then
        
            If Me.Controls("ComboBox" & i).Visible = True Then
            
                If InStr(Me.Controls("ComboBox" & i).Text, "측정방법") <> 0 Then
                
                    MsgBox (Me.Controls("ComboBox" & i).Text & "를 입력하세요.")
                    기본입력.MultiPage1.Value = 1
                    Me.Controls("ComboBox" & i).SetFocus
                    기본입력.Show
                    GoTo 10
                
                End If
            
            End If
        
            If Me.Controls("ComboBox" & i - 1).Visible = True Then
            
                If InStr(Me.Controls("ComboBox" & i - 1).Text, "방식") <> 0 Then
                
                    MsgBox (Me.Controls("ComboBox" & i - 1).Text & "를 입력하세요.")
                    기본입력.MultiPage1.Value = 1
                    Me.Controls("ComboBox" & i - 1).SetFocus
                    기본입력.Show
                    GoTo 10
                
                End If
            
            End If
        
        Else
        
            If Me.Controls("ComboBox" & i).Visible = True Then
            
                If InStr(Me.Controls("ComboBox" & i).Text, "기기") <> 0 Then
                    
                    MsgBox (Me.Controls("ComboBox" & i).Text & "를 입력하세요.")
                    기본입력.MultiPage1.Value = 1
                    Me.Controls("ComboBox" & i).SetFocus
                    기본입력.Show
                    GoTo 10
                
                End If
            
            End If
        
        
        End If
        
    Next i
    
    For i = 1 To 4
    
        If Me.Controls("TextBox" & i).Visible = True Then
        
            If InStr(Me.Controls("TextBox" & i).Text, "측선별 적용") <> 0 Then
                MsgBox (Me.Controls("TextBox" & i).Text & "를 입력하세요.")
                기본입력.MultiPage1.Value = 1
                Me.Controls("TextBox" & i).SetFocus
                기본입력.Show
                GoTo 10
            
            End If
            
        End If
    
    Next i

        
    'Worksheets("종합").Range("N2").Offset(0, 0) = T하천명.Text
    'Worksheets("종합").Range("N3").Offset(0, 0) = T지점명.Text
    'Worksheets("종합").Range("N1").Offset(0, 0) = TDM.Text
    'Worksheets("종합").Range("N4").Offset(0, 0) = T위치.Text
    'Worksheets("종합").Range("B4").Offset(0, 0) = T날짜.Text
    'Worksheets("종합").Range("F4").Offset(0, 0) = T날씨.Text
    'Worksheets("종합").Range("I4").Offset(0, 0) = T바람.Text
    'Worksheets("종합").Range("C26").Offset(0, 0) = T측정자.Text
    'Worksheets("종합").Range("C27").Offset(0, 0) = T비고.Text
    
    'Worksheets("종합").Range("K21").Offset(0, 0) = C종류.Text
    'Worksheets("종합").Range("K22").Offset(0, 0) = C번호.Text
    'Worksheets("이름정의").Range("G11").Offset(0, 0) = C방식.Text '2004/07/13추가
    'Worksheets("종합").Range("K23").Offset(0, 0) = C검정식.Text
    'Worksheets("종합").Range("K24").Offset(0, 0) = C범위.Text
    'Worksheets("종합").Range("K26").Offset(0, 0) = C검정일.Text
    'Worksheets("종합").Range("K27").Offset(0, 0) = C방법.Text
    
    'Worksheets("종합").Range("K15").Offset(0, 0) = T하천수.Text
    'Worksheets("종합").Range("K17").Offset(0, 0) = T유사량.Text
    'Worksheets("종합").Range("K19").Offset(0, 0) = TBio.Text
    
    '******************************************
    '유속계 2개 이상 사용할 수 있도록 코드 수정 2013.11.29 이기성
    '******************************************
    
    If CheckBox1.Value = False Then
        
        Range(Sheets("입력시트").Cells(1, 246), Sheets("입력시트").Cells(10, 250)).ClearContents
        Worksheets("종합").Range("N2").Offset(0, 0) = T하천명.Text
        Worksheets("종합").Range("N3").Offset(0, 0) = T지점명.Text
        Worksheets("종합").Range("N1").Offset(0, 0) = TDM.Text
        Worksheets("종합").Range("N4").Offset(0, 0) = T위치.Text
        Worksheets("종합").Range("B4").Offset(0, 0) = T날짜.Text
        Worksheets("종합").Range("F4").Offset(0, 0) = T날씨.Text
        Worksheets("종합").Range("I4").Offset(0, 0) = T바람.Text
        Worksheets("종합").Range("C26").Offset(0, 0) = T측정자.Text
        Worksheets("종합").Range("C27").Offset(0, 0) = T비고.Text
        Worksheets("종합").Range("K21").Offset(0, 0) = C종류.Text
        Worksheets("이름정의").Range("G11").Offset(0, 0) = C방식.Text '2004/07/13추가
        Worksheets("종합").Range("K27").Offset(0, 0) = C방법.Text
        Worksheets("종합").Range("K15").Offset(0, 0) = T하천수.Text
        Worksheets("종합").Range("K17").Offset(0, 0) = T유사량.Text
        Worksheets("종합").Range("K19").Offset(0, 0) = TBio.Text

        selMeterPara = C번호
                             
        fNoselMeter
                     
        Worksheets("종합").Range("K22").Offset(0, 0) = Worksheets("이름정의").Range("C16").Offset(loc, 0)
        Worksheets("종합").Range("K23").Offset(0, 0) = Worksheets("이름정의").Range("C16").Offset(loc, 1)
        Worksheets("종합").Range("K24").Offset(0, 0) = Worksheets("이름정의").Range("C16").Offset(loc, 8)
        Worksheets("종합").Range("K26").Offset(0, 0) = Worksheets("이름정의").Range("C16").Offset(loc, 9)

    
    
    
    
    
        Select Case Sheets("입력시트").CB_mNum.Text
            Case "M1"  '1번측정한 경우(1차, 2차 구분없음)
                Set rngCell = Worksheets("입력저장1")
            Case "M2"  '2번측정한 경우(2번째 측정한 값 계산 및 저장)
                Set rngCell = Worksheets("입력저장2")
        End Select
        Range(rngCell.Cells(9, 20), rngCell.Cells(108, 20)).ClearContents
        Range(rngCell.Cells(9, 3), rngCell.Cells(108, 20)).Interior.ColorIndex = xlNone
        rngCell.Range("T9").Resize(Application.Count(Range(Sheets("입력시트").Cells(9, 3), Sheets("입력시트").Cells(65536, 3)))) = Sheets("종합").Range("K22")
        rngCell.Columns("T:T").EntireColumn.AutoFit
        
        Unload Me
    Else
                    
        Worksheets("종합").Range("N2").Offset(0, 0) = T하천명.Text
        Worksheets("종합").Range("N3").Offset(0, 0) = T지점명.Text
        Worksheets("종합").Range("N1").Offset(0, 0) = TDM.Text
        Worksheets("종합").Range("N4").Offset(0, 0) = T위치.Text
        Worksheets("종합").Range("B4").Offset(0, 0) = T날짜.Text
        Worksheets("종합").Range("F4").Offset(0, 0) = T날씨.Text
        Worksheets("종합").Range("I4").Offset(0, 0) = T바람.Text
        Worksheets("종합").Range("C26").Offset(0, 0) = T측정자.Text
        Worksheets("종합").Range("C27").Offset(0, 0) = T비고.Text
    
        Worksheets("종합").Range("K15").Offset(0, 0) = T하천수.Text
        Worksheets("종합").Range("K17").Offset(0, 0) = T유사량.Text
        Worksheets("종합").Range("K19").Offset(0, 0) = TBio.Text
        
        Worksheets("종합").Range("K21").Offset(0, 0) = C종류.Text  '종류
        
        For i = 4 To 16 Step 4
            
            If Me.Controls("ComboBox" & i - 3).Visible = True Then
            
                Worksheets("종합").Range("K21").Offset(0, 0) = Worksheets("종합").Range("K21").Offset(0, 0) & Chr(10) & Me.Controls("ComboBox" & i - 3) '종류
        
            End If
        
        Next i
        
        Worksheets("종합").Range("K22").Offset(0, 0) = C번호.Text  '유속계 번호
        
        For i = 4 To 16 Step 4
            
            If Me.Controls("ComboBox" & i - 2).Visible = True Then
            
                Worksheets("종합").Range("K22").Offset(0, 0) = Worksheets("종합").Range("K22").Offset(0, 0) & Chr(10) & Me.Controls("ComboBox" & i - 2) '유속계 번호
        
            End If
        
        Next i
        
        Worksheets("종합").Range("K27").Offset(0, 0) = C방법.Text  '측정방법
        
        For i = 4 To 16 Step 4
            
            If Me.Controls("ComboBox" & i).Visible = True Then
            
                Worksheets("종합").Range("K27").Offset(0, 0) = Worksheets("종합").Range("K27").Offset(0, 0) & Chr(10) & Me.Controls("ComboBox" & i) '측정방법
        
            End If
        
        Next i
        
        
        selMeterPara = C번호.Text
        fNoselMeter
        Worksheets("종합").Range("K22").Offset(0, 0) = Worksheets("이름정의").Range("C16").Offset(loc, 0)
        Worksheets("종합").Range("K23").Offset(0, 0) = Worksheets("이름정의").Range("C16").Offset(loc, 1)
        Worksheets("종합").Range("K24").Offset(0, 0) = Worksheets("이름정의").Range("C16").Offset(loc, 8)
        Worksheets("종합").Range("K26").Offset(0, 0) = Worksheets("이름정의").Range("C16").Offset(loc, 9)
        
        For i = 4 To 16 Step 4
            
            If Me.Controls("ComboBox" & i - 2).Visible = True Then
            
                selMeterPara = Me.Controls("ComboBox" & i - 2).Text
                             
                fNoselMeter
                     
                Worksheets("종합").Range("K22").Offset(0, 0) = Worksheets("종합").Range("K22").Offset(0, 0) & Chr(10) & Worksheets("이름정의").Range("C16").Offset(loc, 0)
                Worksheets("종합").Range("K23").Offset(0, 0) = Worksheets("종합").Range("K23").Offset(0, 0) & Chr(10) & Worksheets("이름정의").Range("C16").Offset(loc, 1)
                Worksheets("종합").Range("K24").Offset(0, 0) = Worksheets("종합").Range("K24").Offset(0, 0) & Chr(10) & Worksheets("이름정의").Range("C16").Offset(loc, 8)
                Worksheets("종합").Range("K26").Offset(0, 0) = Worksheets("종합").Range("K26").Offset(0, 0) & Chr(10) & Worksheets("이름정의").Range("C16").Offset(loc, 9)
            
            End If
        
        Next i
        
        Range(Sheets("입력시트").Cells(1, 246), Sheets("입력시트").Cells(10, 250)).ClearContents
        
        With Sheets("입력시트")
                        
            .Cells(1, 246) = C종류.Text
            .Cells(1, 247) = C번호.Text
            .Cells(1, 248) = C방식.Text
            .Cells(1, 249) = C방법.Text
            
        
        n = 0
        
        Do
         
            n = n + 1
            
            If Me.Controls("Combobox" & 4 * n - 3).Visible = True Then
            
                For i = 1 To 4
                
                    .Cells(n + 1, 245 + i) = Me.Controls("Combobox" & 4 * (n - 1) + i).Text
            
                Next i
            
                .Cells(n + 1, 245 + i) = Me.Controls("Textbox" & n).Text
                
            End If
            
        Loop Until n = 4
                
        End With
            
        유속계입력
            
        Unload Me
    End If
    
    
        
End Sub


Private Sub T지점명_KeyDown(ByVal KeyCode As MSForms.ReturnInteger, ByVal Shift As Integer)

If KeyCode = 13 Or KeyCode = 9 Then

    지점입력

    If 기본입력.TDM = Empty Then
        
        KeyCode = vbKeyShift + vbKeyTab
        
        
        
    Else
        기본입력.TDM.SetFocus
    
    End If
    
End If



End Sub

