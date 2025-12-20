' Module: Module2.bas
' Stream: _VBA_PROJECT_CUR/VBA/Module2
' Source: C:\Users\rando\repos\reAA\경주대종천하류보20250501.xls
' ============================================================

Attribute VB_Name = "Module2"
Public sh
Option Base 1
Public Matrix As Variant
Public i
Public Sub 거리계산()
        
        With Sheets(sh)
            Dim Dis(), Dis1() As Variant
            Dim n, i
                        
            n = 0
            
            Do
                n = n + 1
            Loop Until Len(.Cells(8, 3).Offset(n + 1, 0)) = 0
                                                
                                                
            Dis = Range(.Cells(9, 4), .Cells(8, 4).Offset(n + 1, 0))
                        
            n = 0
            Do
                n = n + 1
                
                If Application.CountIf(Sheets("입력시트").Range("D9:D108"), Dis(n, 1)) > 1 Then
                    i = i + 1
                End If
                
            Loop Until Len(Dis(n + 1, 1)) = 0
            
            
            If i > 0 Then
            
                ReDim Dis1(n, 1)
                
                Dis1(1, 1) = 0
                
                n = 1
                
                Do
                
                    n = n + 1
                    
                    Dis1(n, 1) = Dis1(n - 1, 1) + Dis(n, 1)
                
                Loop Until Len(Dis(n + 1, 1)) = 0
                
                Range(.Cells(9, 4), .Cells(9, 4).Offset(n - 1, 0)) = Dis1()
            End If
            
        End With
'수정내용
'1.누가거리인지 이동거리인지 파악하는 방법 수정
'  Countif 사용하여 각 거리별 중복여부 확인후 같은 값이 2개 이상일 경우 중복으로 판단
'  i 값이 1이상일 경우 구간거리로 판단 '2014년 02월 10일 이기성 수정
    End Sub

Public Sub 지점입력()

ReDim Matrix(i + 1, 2)
    
i = 0
    
    Do
        
        n = n + 1
        
        If Sheets("수위관측소일람표").Cells(n, 2) = 기본입력.T지점명.Text Then
            
            i = i + 1
            Matrix(i, 1) = Sheets("수위관측소일람표").Cells(n, 1) & "_" 'DM No.
            Matrix(i, 2) = Sheets("수위관측소일람표").Cells(n, 3) '하천명
        
        End If
    
    Loop Until Len(Sheets("수위관측소일람표").Cells(n + 1, 2)) = 0

    If i > 1 Then
        
        중복정보.Left = 100
        중복정보.Show
    
    ElseIf i = 1 Then
        
        기본입력.T하천명 = Matrix(i, 2)
        기본입력.TDM = Matrix(i, 1)
        
   Else
        
        MsgBox (기본입력.T지점명 & " 지점으로 검색된 관측소는 존재하지 않습니다. 지점명을 다시 입력하십시오!")
                
        기본입력.T하천명 = Empty
        기본입력.TDM = Empty
        
    End If
   
    
    

End Sub
Public Sub 유속계입력()

    Dim 유속계(), col(), Pri() As Variant
    Dim 평균, P_i, P_j, P_k, tex, Count_Total, Stepp, Count_Text


Set rng1 = Sheets("입력시트")

Count_Total = Application.Count(Range(rng1.Cells(9, 3), rng1.Cells(65536, 3)))

ReDim 유속계(Count_Total, 1)
ReDim col(Count_Total, 1)
'ReDim Pri((.Controls.Count - 3) / 2, 1)

기본입력.Hide

Pri = Range(rng1.Cells(2, 250), rng1.Cells(10, 250))

Count_Text = 0

For P_i = 1 To 4

    If 기본입력.Controls("TextBox" & P_i).Visible = True Then
    
        Count_Text = Count_Text + 1
    
    ElseIf Len(rng1.Cells(P_i + 1, 250)) <> 0 Then
        
        Count_Text = Count_Text + 1
    
    End If
    

Next P_i

'For P_i = 1 To Application.Count(Range(Sheets("입력시트").Cells(1, 250), Sheets("입력시트").Cells(10, 250)))
    
    'Pri(P_i, 1) = .Controls("Textbox" & P_i + 1).Text

'Next P_i

For P_i = 1 To Count_Text
    
    tex = Pri(P_i, 1)
    
    If Len(tex) = 0 Then
        
        MsgBox (rng1.Cells(P_i + 1, 247) & "유속계에 대한 측선 설정이 없습니다.")
        
        기본입력.MultiPage1.Value = 1
        기본입력.Controls("TextBox" & P_i).SetFocus
        기본입력.Show
        
        GoTo 10
        
    End If
    
    Do
        If InStr(tex, ",") <> 0 Then
            
            P_j = Left(tex, InStr(tex, ",") - 1)
            
            If InStr(P_j, "-") = 0 Then
                
                If Val(P_j) > Count_Total Then
                
                    MsgBox (P_j & "번 측선은 최대측선(" & Count_Total & ")을 벗어납니다.")
                
                    기본입력.MultiPage1.Value = 1
                    기본입력.Controls("TextBox" & P_i).SetFocus
                    기본입력.Show
                                
                    GoTo 10
                                
                End If
                
                
                If Len(유속계(P_j, 1)) = 0 Then
                    
                    유속계(P_j, 1) = rng1.Cells(P_i + 1, 247)
                    
                    col(P_j, 1) = P_i + 33
                
                Else
                    
                    MsgBox (P_j & "번 측선에 중복된 유속계가 설정되었습니다. 측선을 다시한번 확인하세요")
                    
                    기본입력.MultiPage1.Value = 1
                    기본입력.Controls("TextBox" & P_i).SetFocus
                    기본입력.Show
                
                    GoTo 10
                
                End If
                
                tex = Right(tex, Len(tex) - InStr(tex, ","))
            
            Else
                
                If InStr(P_j, "-") <> 0 Then
                                                            
                    If Val(Left(P_j, InStr(P_j, "-") - 1)) - Val(Right(P_j, Len(P_j) - InStr(P_j, "-"))) > 0 Then
                
                        Stepp = -1
                    
                    Else
                
                        Stepp = 1
                
                    End If
                
                End If
                
                For P_k = Left(P_j, InStr(P_j, "-") - 1) To Right(P_j, Len(P_j) - InStr(P_j, "-")) Step Stepp
                    
                    If Val(P_k) > Count_Total Then
                
                        MsgBox (P_k & "번 측선은 최대측선(" & Count_Total & ")을 벗어납니다.")
                
                        기본입력.MultiPage1.Value = 1
                        기본입력.Controls("TextBox" & P_i).SetFocus
                        기본입력.Show
                                
                        GoTo 10
                                
                    End If
                    
                    If Len(유속계(P_k, 1)) = 0 Then
                        
                        유속계(P_k, 1) = rng1.Cells(P_i + 1, 247)
                        
                        col(P_k, 1) = P_i + 33
                    
                    Else
                        
                        MsgBox (P_k & "번 측선에 중복된 유속계가 설정되었습니다. 측선을 다시한번 확인하세요")
                        
                        기본입력.MultiPage1.Value = 1
                        기본입력.Controls("TextBox" & P_i).SetFocus
                        기본입력.Show
                    
                        GoTo 10
                    
                    End If
                
                Next P_k
                
                tex = Right(tex, Len(tex) - InStr(tex, ","))
            
            End If
        
        End If
    
    Loop Until InStr(tex, ",") = 0
    
    If InStr(tex, "-") = 0 Then
    
        If Val(tex) > Count_Total Then
                
            MsgBox (tex & "번 측선은 최대측선(" & Count_Total & ")을 벗어납니다.")
                
            기본입력.MultiPage1.Value = 1
            기본입력.Controls("TextBox" & P_i).SetFocus
            기본입력.Show
                                
            GoTo 10
                                
        End If
        
        If Len(유속계(tex, 1)) = 0 Then
            
            유속계(tex, 1) = rng1.Cells(P_i + 1, 247)
            
            col(tex, 1) = P_i + 33
        
        Else
            
            MsgBox (tex & "번 측선에 중복된 유속계가 설정되었습니다. 측선을 다시한번 확인하세요")
            
            기본입력.MultiPage1.Value = 1
            기본입력.Controls("TextBox" & P_i).SetFocus
            기본입력.Show
        
            GoTo 10
        
        End If
    
    Else
        
        
        If InStr(tex, "-") <> 0 Then
        
            If Val(Left(tex, InStr(tex, "-") - 1)) - Val(Right(tex, Len(tex) - InStr(tex, "-"))) > 0 Then
                
                Stepp = -1
                    
            Else
                
                Stepp = 1
                
            End If
        
        End If
        
        For P_k = Left(tex, InStr(tex, "-") - 1) To Right(tex, Len(tex) - InStr(tex, "-")) Step Stepp
            
            If Val(P_k) > Count_Total Then
                
                MsgBox (P_k & "번 측선은 최대측선(" & Count_Total & ")을 벗어납니다.")
                
                기본입력.MultiPage1.Value = 1
                기본입력.Controls("TextBox" & P_i).SetFocus
                기본입력.Show
                
                GoTo 10
                                
            End If
            
            If Len(유속계(P_k, 1)) = 0 Then
                
                유속계(P_k, 1) = rng1.Cells(P_i + 1, 247)
                
                col(P_k, 1) = P_i + 33
            
            Else
                
                MsgBox (P_k & "번 측선에 중복된 유속계가 설정되었습니다. 측선을 다시한번 확인하세요")
                
                기본입력.MultiPage1.Value = 1
                기본입력.Controls("TextBox" & P_i).SetFocus
                기본입력.Show
                
                GoTo 10
            
            End If
        
        Next P_k
    
    End If

Next P_i

P_k = 0

Do
    P_k = P_k + 1
    
    If Len(유속계(P_k, 1)) = 0 Then
        유속계(P_k, 1) = Left(Sheets("종합").Range("K22"), InStr(Sheets("종합").Range("K22"), Chr(10)) - 1)
    End If
    
Loop Until P_k = Count_Total

'*********************************
'*유속계 설정 끝
'*해당시트에 유속계 설정 정보 출력
'*********************************
    
    Select Case Sheets("입력시트").CB_mNum.Text
        Case "M1"  '1번측정한 경우(1차, 2차 구분없음)
            Set rngCell = Worksheets("입력저장1")
        Case "M2"  '2번측정한 경우(2번째 측정한 값 계산 및 저장)
            Set rngCell = Worksheets("입력저장2")
    End Select
Range(rngCell.Cells(9, 20), rngCell.Cells(108, 20)).ClearContents
Range(rngCell.Cells(9, 20), rngCell.Cells(9 + Count_Total - 1, 20)) = 유속계
Range(rngCell.Cells(9, 3), rngCell.Cells(108, 20)).Interior.ColorIndex = xlNone
rngCell.Columns("T:T").EntireColumn.AutoFit

P_k = 8

Do
    P_k = P_k + 1
    
    If Len(col(P_k - 8, 1)) <> 0 Then
        Range(rngCell.Cells(P_k, 3), rngCell.Cells(P_k, 20)).Interior.ColorIndex = col(P_k - 8, 1)
    End If
    
Loop Until P_k - 8 = Count_Total

10


End Sub


