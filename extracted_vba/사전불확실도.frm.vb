' Module: 사전불확실도.frm
' Stream: _VBA_PROJECT_CUR/VBA/사전불확실도
' Source: C:\Users\rando\repos\reAA\경주대종천하류보20250501.xls
' ============================================================

Attribute VB_Name = "사전불확실도"
Attribute VB_Base = "0{FAC3AD6F-37B9-428B-A68D-85F2250E943F}{A202E51D-F09D-42D1-959C-2DCEF194D1E6}"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Attribute VB_TemplateDerived = False
Attribute VB_Customizable = False

Private Sub C종료_Click()
    Unload Me
End Sub

Private Sub C계산_Click()
    Dim tnumV As Integer
    Dim teT As Double
    Dim tnumP As Integer
    Dim tmV As Double
    Dim tQ As Double
    
    Dim Xb As Double
    Dim Xd As Double
    
    Dim Xe As Variant
    Dim Xp As Variant
    Dim Xc As Variant
    Dim Xm As Variant
    
    Dim X2b As Double
    Dim X2d As Double
    Dim X2c As Double
    
    Dim X1Q As Double
    Dim X2Q As Double
    Dim XQ As Double
    
    Dim tiq As Double
    Dim sumOver As Double
    Dim sumBelow As Double
    
    tnumV = T측선수.Text
    teT = T측정시간.Text
    tnumP = T측점수.Text
    tmV = T평균유속.Text
    tQ = T유량.Text

    Xb = 0.1
    Xd = 1
    
    Xe = Xe_Error(tnumP, teT, tmV)
    Xp = Xp_Error(tnumP)
    Xc = Xc_Error(tmV)
    Xm = Xm_Error(tnumV)
    
    X2b = 0.5
    X2d = 0.5
    X2c = 1#
    
'*************************************************************************************
'   tQ=∑(tiq), tiq=bi×di×vi
'   측선별 유량이 등유량이라 가정하면
'   (tiq_1=tiq_2=tiq_3=...=tiq_n)=tQ/n 이다.
'   그리고  모든 측선에 대한 Xb, Xd ,Xe, Xp, Xc의 평균치가 취해 졌다면(모든 측선의
'   조건이 동일하다고 가정)
    tiq = tQ / tnumV
    For i = 1 To tnumV
        sumOver = sumOver + ((tiq ^ 2) * (Xb ^ 2 + Xd ^ 2 + Xe ^ 2 + Xp ^ 2 + Xc ^ 2))
        sumBelow = sumBelow + tiq   '=tQ
    Next i
    X1Q = (Xm ^ 2 + sumOver / (sumBelow ^ 2)) ^ 0.5
    
'   n>10이고 위의 조건에 부합할 경우의 간략식
'   X1Q = (Xm ^ 2 + (Xb ^ 2 + Xd ^ 2 + Xe ^ 2 + Xp ^ 2 + Xc ^ 2) / tnumV) ^ 0.5
    
    X2Q = (X2b ^ 2 + X2d ^ 2 + X2c ^ 2) ^ 0.5
    XQ = (X1Q ^ 2 + X2Q ^ 2) ^ 0.5
        
    TO유량.Text = Format(tQ, "###0.0000")
    T무작위.Text = Format(X1Q, "###0.00")
    T계통.Text = Format(X2Q, "###0.00")
    T전체.Text = Format(XQ, "###0.00")

End Sub
Function Xe_Error(fNpoint As Integer, fT As Double, fVel As Double) As Variant
'****************************************************************
' 프라이스 유속계
' 측정시간에 따른 무작위 불확실도 X'e 구하기
' 유속2의 경우에 사용
' 2003. 5.
' 황석환
' y=(a*b+c*x^d)/(b+x^d)           y=Xei, x=vi
'****************************************************************
  Dim j As Integer
  Dim k As Double
  Dim vi As Double
'****************************************************************
  j = fNpoint     ' 측점수
'****************************************************************
  k = fT     ' 측정시간
  vi = fVel    ' 평균유속
'****************************************************************
' 0.2D, 0.4D or 0.6D
'********************
     If k <= 0.5 Then
            If vi <= 0.05 Then
                    rLow = Worksheets("para").Range("B8").Offset(0, 1)
            ElseIf vi > 1 Then
                    rLow = Worksheets("para").Range("B15").Offset(0, 1)
            Else
                For ii = 0 To 5
                    If (vi > Worksheets("para").Range("B8").Offset(ii, 0)) And vi <= Worksheets("para").Range("B8").Offset(ii + 1, 0) Then
                        x1 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x2 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y1 = Worksheets("para").Range("B8").Offset(ii, 1)
                        y2 = Worksheets("para").Range("B8").Offset(ii + 1, 1)
                        rLow = (y2 - y1) / (x2 - x1) * (vi - x2) + y2
                    End If
                Next ii
            End If
     
     ElseIf (k > 0.5 And k < 1) Then
            If vi <= 0.05 Then
                    rPar1 = Worksheets("para").Range("B8").Offset(0, 1)
                    rPar2 = Worksheets("para").Range("B8").Offset(0, 2)
            ElseIf vi > 1 Then
                    rPar1 = Worksheets("para").Range("B15").Offset(0, 1)
                    rPar2 = Worksheets("para").Range("B15").Offset(0, 2)
            Else
                For ii = 0 To 5
                    If (vi > Worksheets("para").Range("B8").Offset(ii, 0)) And vi <= Worksheets("para").Range("B8").Offset(ii + 1, 0) Then
                        x11 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x12 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y11 = Worksheets("para").Range("B8").Offset(ii, 1)
                        y12 = Worksheets("para").Range("B8").Offset(ii + 1, 1)
                        rPar1 = (y12 - y11) / (x12 - x11) * (vi - x12) + y12
                    
                        x21 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x22 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y21 = Worksheets("para").Range("B8").Offset(ii, 2)
                        y22 = Worksheets("para").Range("B8").Offset(ii + 1, 2)
                        rPar2 = (y22 - y21) / (x22 - x21) * (vi - x22) + y22
                    End If
                Next ii
            End If
            rLow = rPar2 - (rPar2 - rPar1) * (1 - k) / (1 - 0.5)
     
     ElseIf k = 1 Then
            If vi <= 0.05 Then
                    rLow = Worksheets("para").Range("B8").Offset(0, 2)
            ElseIf vi > 1 Then
                    rLow = Worksheets("para").Range("B15").Offset(0, 2)
            Else
                For ii = 0 To 5
                    If (vi > Worksheets("para").Range("B8").Offset(ii, 0)) And vi <= Worksheets("para").Range("B8").Offset(ii + 1, 0) Then
                        x1 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x2 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y1 = Worksheets("para").Range("B8").Offset(ii, 2)
                        y2 = Worksheets("para").Range("B8").Offset(ii + 1, 2)
                        rLow = (y2 - y1) / (x2 - x1) * (vi - x2) + y2
                    End If
                Next ii
            End If
     
     ElseIf (k > 1 And k < 2) Then
            If vi <= 0.05 Then
                    rPar1 = Worksheets("para").Range("B8").Offset(0, 2)
                    rPar2 = Worksheets("para").Range("B8").Offset(0, 3)
            ElseIf vi > 1 Then
                    rPar1 = Worksheets("para").Range("B15").Offset(0, 2)
                    rPar2 = Worksheets("para").Range("B15").Offset(0, 3)
            Else
                For ii = 0 To 5
                    If (vi > Worksheets("para").Range("B8").Offset(ii, 0)) And vi <= Worksheets("para").Range("B8").Offset(ii + 1, 0) Then
                        x11 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x12 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y11 = Worksheets("para").Range("B8").Offset(ii, 2)
                        y12 = Worksheets("para").Range("B8").Offset(ii + 1, 2)
                        rPar1 = (y12 - y11) / (x12 - x11) * (vi - x12) + y12
                    
                        x21 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x22 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y21 = Worksheets("para").Range("B8").Offset(ii, 3)
                        y22 = Worksheets("para").Range("B8").Offset(ii + 1, 3)
                        rPar2 = (y22 - y21) / (x22 - x21) * (vi - x22) + y22
                    End If
                Next ii
            End If
            rLow = rPar2 - (rPar2 - rPar1) * (2 - k) / (2 - 1)
     
     ElseIf k = 2 Then
            If vi <= 0.05 Then
                    rLow = Worksheets("para").Range("B8").Offset(0, 3)
            ElseIf vi > 1 Then
                    rLow = Worksheets("para").Range("B15").Offset(0, 3)
            Else
                For ii = 0 To 5
                    If (vi > Worksheets("para").Range("B8").Offset(ii, 0)) And vi <= Worksheets("para").Range("B8").Offset(ii + 1, 0) Then
                        x1 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x2 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y1 = Worksheets("para").Range("B8").Offset(ii, 3)
                        y2 = Worksheets("para").Range("B8").Offset(ii + 1, 3)
                        rLow = (y2 - y1) / (x2 - x1) * (vi - x2) + y2
                    End If
                Next ii
            End If
     
     ElseIf (k > 2 And k < 3) Then
            If vi <= 0.05 Then
                    rPar1 = Worksheets("para").Range("B8").Offset(0, 3)
                    rPar2 = Worksheets("para").Range("B8").Offset(0, 4)
            ElseIf vi > 1 Then
                    rPar1 = Worksheets("para").Range("B15").Offset(0, 3)
                    rPar2 = Worksheets("para").Range("B15").Offset(0, 4)
            Else
                For ii = 0 To 5
                    If (vi > Worksheets("para").Range("B8").Offset(ii, 0)) And vi <= Worksheets("para").Range("B8").Offset(ii + 1, 0) Then
                        x11 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x12 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y11 = Worksheets("para").Range("B8").Offset(ii, 3)
                        y12 = Worksheets("para").Range("B8").Offset(ii + 1, 3)
                        rPar1 = (y12 - y11) / (x12 - x11) * (vi - x12) + y12
                    
                        x21 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x22 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y21 = Worksheets("para").Range("B8").Offset(ii, 4)
                        y22 = Worksheets("para").Range("B8").Offset(ii + 1, 4)
                        rPar2 = (y22 - y21) / (x22 - x21) * (vi - x22) + y22
                    End If
                Next ii
            End If
            rLow = rPar2 - (rPar2 - rPar1) * (3 - k) / (3 - 2)
        
     ElseIf k >= 3 Then
            If vi <= 0.05 Then
                    rLow = Worksheets("para").Range("B8").Offset(0, 4)
            ElseIf vi > 1 Then
                    rLow = Worksheets("para").Range("B15").Offset(0, 4)
            Else
                For ii = 0 To 5
                    If (vi > Worksheets("para").Range("B8").Offset(ii, 0)) And vi <= Worksheets("para").Range("B8").Offset(ii + 1, 0) Then
                        x1 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x2 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y1 = Worksheets("para").Range("B8").Offset(ii, 4)
                        y2 = Worksheets("para").Range("B8").Offset(ii + 1, 4)
                        rLow = (y2 - y1) / (x2 - x1) * (vi - x2) + y2
                    End If
                Next ii
            End If
     Else
             outp.Offset(i, 0) = "error"
     End If
'****************************************************************
' 0.8D, 0.9D
'********************
     If k <= 0.5 Then
            If vi <= 0.05 Then
                    rHigh = Worksheets("para").Range("B8").Offset(0, 5)
            ElseIf vi > 1 Then
                    rHigh = Worksheets("para").Range("B15").Offset(0, 5)
            Else
                For ii = 0 To 5
                    If (vi > Worksheets("para").Range("B8").Offset(ii, 0)) And vi <= Worksheets("para").Range("B8").Offset(ii + 1, 0) Then
                        x1 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x2 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y1 = Worksheets("para").Range("B8").Offset(ii, 5)
                        y2 = Worksheets("para").Range("B8").Offset(ii + 1, 5)
                        rHigh = (y2 - y1) / (x2 - x1) * (vi - x2) + y2
                    End If
                Next ii
            End If
     
     ElseIf (k > 0.5 And k < 1) Then
            If vi <= 0.05 Then
                    rPar1 = Worksheets("para").Range("B8").Offset(0, 5)
                    rPar2 = Worksheets("para").Range("B8").Offset(0, 6)
            ElseIf vi > 1 Then
                    rPar1 = Worksheets("para").Range("B15").Offset(0, 5)
                    rPar2 = Worksheets("para").Range("B15").Offset(0, 6)
            Else
                For ii = 0 To 5
                    If (vi > Worksheets("para").Range("B8").Offset(ii, 0)) And vi <= Worksheets("para").Range("B8").Offset(ii + 1, 0) Then
                        x11 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x12 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y11 = Worksheets("para").Range("B8").Offset(ii, 5)
                        y12 = Worksheets("para").Range("B8").Offset(ii + 1, 5)
                        rPar1 = (y12 - y11) / (x12 - x11) * (vi - x12) + y12
                    
                        x21 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x22 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y21 = Worksheets("para").Range("B8").Offset(ii, 6)
                        y22 = Worksheets("para").Range("B8").Offset(ii + 1, 6)
                        rPar2 = (y22 - y21) / (x22 - x21) * (vi - x22) + y22
                    End If
                Next ii
            End If
            rHigh = rPar2 - (rPar2 - rPar1) * (1 - k) / (1 - 0.5)
     
     ElseIf k = 1 Then
            If vi <= 0.05 Then
                    rHigh = Worksheets("para").Range("B8").Offset(0, 6)
            ElseIf vi > 1 Then
                    rHigh = Worksheets("para").Range("B15").Offset(0, 6)
            Else
                For ii = 0 To 5
                    If (vi > Worksheets("para").Range("B8").Offset(ii, 0)) And vi <= Worksheets("para").Range("B8").Offset(ii + 1, 0) Then
                       x1 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x2 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y1 = Worksheets("para").Range("B8").Offset(ii, 6)
                        y2 = Worksheets("para").Range("B8").Offset(ii + 1, 6)
                        rHigh = (y2 - y1) / (x2 - x1) * (vi - x2) + y2
                    End If
                Next ii
            End If
     
     ElseIf (k > 1 And k < 2) Then
            If vi <= 0.05 Then
                    rPar1 = Worksheets("para").Range("B8").Offset(0, 6)
                    rPar2 = Worksheets("para").Range("B8").Offset(0, 7)
            ElseIf vi > 1 Then
                    rPar1 = Worksheets("para").Range("B15").Offset(0, 6)
                    rPar2 = Worksheets("para").Range("B15").Offset(0, 7)
            Else
                For ii = 0 To 5
                    If (vi > Worksheets("para").Range("B8").Offset(ii, 0)) And vi <= Worksheets("para").Range("B8").Offset(ii + 1, 0) Then
                        x11 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x12 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y11 = Worksheets("para").Range("B8").Offset(ii, 6)
                        y12 = Worksheets("para").Range("B8").Offset(ii + 1, 6)
                        rPar1 = (y12 - y11) / (x12 - x11) * (vi - x12) + y12
                    
                        x21 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x22 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y21 = Worksheets("para").Range("B8").Offset(ii, 7)
                        y22 = Worksheets("para").Range("B8").Offset(ii + 1, 7)
                        rPar2 = (y22 - y21) / (x22 - x21) * (vi - x22) + y22
                    End If
                Next ii
            End If
            rHigh = rPar2 - (rPar2 - rPar1) * (2 - k) / (2 - 1)
     
     ElseIf k = 2 Then
            If vi <= 0.05 Then
                    rHigh = Worksheets("para").Range("B8").Offset(0, 7)
            ElseIf vi > 1 Then
                    rHigh = Worksheets("para").Range("B15").Offset(0, 7)
            Else
                For ii = 0 To 5
                    If (vi > Worksheets("para").Range("B8").Offset(ii, 0)) And vi <= Worksheets("para").Range("B8").Offset(ii + 1, 0) Then
                        x1 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x2 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y1 = Worksheets("para").Range("B8").Offset(ii, 7)
                        y2 = Worksheets("para").Range("B8").Offset(ii + 1, 7)
                        rHigh = (y2 - y1) / (x2 - x1) * (vi - x2) + y2
                    End If
                Next ii
            End If
     
     ElseIf (k > 2 And k < 3) Then
            If vi <= 0.05 Then
                    rPar1 = Worksheets("para").Range("B8").Offset(0, 7)
                    rPar2 = Worksheets("para").Range("B8").Offset(0, 8)
            ElseIf vi > 1 Then
                    rPar1 = Worksheets("para").Range("B15").Offset(0, 7)
                    rPar2 = Worksheets("para").Range("B15").Offset(0, 8)
            Else
                For ii = 0 To 5
                    If (vi > Worksheets("para").Range("B8").Offset(ii, 0)) And vi <= Worksheets("para").Range("B8").Offset(ii + 1, 0) Then
                        x11 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x12 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y11 = Worksheets("para").Range("B8").Offset(ii, 7)
                        y12 = Worksheets("para").Range("B8").Offset(ii + 1, 7)
                        rPar1 = (y12 - y11) / (x12 - x11) * (vi - x12) + y12
                    
                        x21 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x22 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y21 = Worksheets("para").Range("B8").Offset(ii, 8)
                        y22 = Worksheets("para").Range("B8").Offset(ii + 1, 8)
                        rPar2 = (y22 - y21) / (x22 - x21) * (vi - x22) + y22
                    End If
                Next ii
            End If
            rHigh = rPar2 - (rPar2 - rPar1) * (3 - k) / (3 - 2)
        
     ElseIf k >= 3 Then
            If vi <= 0.05 Then
                    rHigh = Worksheets("para").Range("B8").Offset(0, 8)
            ElseIf vi > 1 Then
                    rHigh = Worksheets("para").Range("B15").Offset(0, 8)
            Else
                For ii = 0 To 5
                    If (vi > Worksheets("para").Range("B8").Offset(ii, 0)) And vi <= Worksheets("para").Range("B8").Offset(ii + 1, 0) Then
                        x1 = Worksheets("para").Range("B8").Offset(ii, 0)
                        x2 = Worksheets("para").Range("B8").Offset(ii + 1, 0)
                        y1 = Worksheets("para").Range("B8").Offset(ii, 8)
                        y2 = Worksheets("para").Range("B8").Offset(ii + 1, 8)
                        rHigh = (y2 - y1) / (x2 - x1) * (vi - x2) + y2
                    End If
                Next ii
            End If
     Else
             Xe_Error = "error"
     End If
'****************************************************************
' 불확실도
'********************
     Select Case j
        Case Is = 1
            Xe_Error = rLow                    '0.6D
        Case Is = 2
            Xe_Error = (rLow + rHigh) / 2      '0.2D, 0.8D
        Case Is = 3
            Xe_Error = (2 * rLow + rHigh) / 3  '0.2D, 0.6D, 0.8D
        Case Else
            Xe_Error = "Not 1,2,3점법"
     End Select
End Function
Function Xp_Error(fNpoint As Integer) As Variant
'****************************************************************
' 측선에서의 측점수에 따른 무작위 불확실도 X'p 구하기
' 2003. 1.
' 황석환
'****************************************************************
  Dim k As Integer

'****************************************************************
  k = fNpoint     ' 측점수
'****************************************************************
     Select Case k
        Case Is = 1
            Xp_Error = 15
        Case Is = 2
            Xp_Error = 7
        Case Is = 3
            Xp_Error = 19 / 3
        Case Else
            Xp_Error = "Not 1,2,3점법"
     End Select
End Function
Function Xc_Error(fVel As Double) As Variant
'****************************************************************
' 유속계 검정에 따른 무작위 불확실도 X'c 구하기
' 2003. 1.
' 황석환
' y=a-b*exp(-c*x^d)           y=Xci, x=vi
'****************************************************************
    Dim vi As Double
'****************************************************************
     vi = fVel    ' 평균유속
'****************************************************************
     Select Case vi
        Case Is < 0.03
            Xc_Error = Worksheets("para").Range("B34").Offset(0, 1)
        Case Is > 0.5
            Xc_Error = Worksheets("para").Range("B39").Offset(0, 1)
        Case Else
            For ii = 0 To 4
                If (vi > Worksheets("para").Range("B34").Offset(ii, 0)) And vi <= Worksheets("para").Range("B34").Offset(ii + 1, 0) Then
                    x1 = Worksheets("para").Range("B34").Offset(ii, 0)
                    x2 = Worksheets("para").Range("B34").Offset(ii + 1, 0)
                    y1 = Worksheets("para").Range("B34").Offset(ii, 1)
                    y2 = Worksheets("para").Range("B34").Offset(ii + 1, 1)
                    rXc = (y2 - y1) / (x2 - x1) * (vi - x2) + y2
                End If
            Next ii
            Xc_Error = rXc
     End Select
End Function
Function Xm_Error(nVel As Integer) As Variant
'****************************************************************
' 측선수에 따른 무작위 불확실도 X'm 구하기
' 2003. 1.
' 황석환
' y=a+bx+cx^2+dx^3+ex^4+fx^5+gx^6           y=Xmi, x=측선수(nV)
'****************************************************************
  Dim nV As Integer
  nV = nVel    ' nV=유속측선의 수
'****************************************************************
  Select Case nV
    Case Is < 5
        Xm_Error = Worksheets("para").Range("B52").Offset(0, 1)
    Case Is > 35
        Xm_Error = Worksheets("para").Range("B60").Offset(0, 1)
    Case Else
        For ii = 0 To 6
            If (nV > Worksheets("para").Range("B52").Offset(ii, 0)) And nV <= Worksheets("para").Range("B52").Offset(ii + 1, 0) Then
                x1 = Worksheets("para").Range("B52").Offset(ii, 0)
                x2 = Worksheets("para").Range("B52").Offset(ii + 1, 0)
                y1 = Worksheets("para").Range("B52").Offset(ii, 1)
                y2 = Worksheets("para").Range("B52").Offset(ii + 1, 1)
                rXm = (y2 - y1) / (x2 - x1) * (nV - x2) + y2
            End If
        Next ii
        Xm_Error = rXm
  End Select
End Function

