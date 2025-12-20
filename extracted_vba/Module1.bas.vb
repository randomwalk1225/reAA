' Module: Module1.bas
' Stream: _VBA_PROJECT_CUR/VBA/Module1
' Source: C:\Users\rando\repos\reAA\경주대종천하류보20250501.xls
' ============================================================

Attribute VB_Name = "Module1"
Public selMeterPara, loc ' As Range


Sub LoadTextFile()
    Dim TexName As String '입력화일네임
    Dim strData As String '한줄저장 문자열변수
    Dim rngImport As Range
    Dim r As Long

    Application.DisplayAlerts = False
    
    Close #1
    '*******************************************
    'File명 입력상자
    TexName = Application.GetOpenFilename("Text Files(*.csv),*.csv")
    '*******************************************
    Open TexName For Input Access Read As #1
    
    For Each sht In Sheets
        If sht.Name = "ImportCSV" Then
            MsgBox "같은 이름의 시트가 이미 있으나 삭제하겠습니다", , "시트 삭제"
            sht.Delete
        End If
    Next sht
        
    Worksheets.Add.Name = "ImportCSV"
    Worksheets("ImportCSV").Visible = False
    
    Set rngImport = Worksheets("ImportCSV").Range("A1")
    
    r = 0
    Do While Not EOF(1)
        Line Input #1, strData

        strTemp = ""
        For i = 1 To Len(strData)
            strText = Mid(strData, i, 1)
            If strText = "," Or i = Len(strData) Then
                '**********************************************
                '    마지막한자리가 짤리지 않게 하기 위함
                '**********************************************
                If i = Len(strData) Then
                    If strText <> Chr(34) Then  '공백문자열의 경우 ""으로 출력되는데 이것을 삭제하기위함
                        strTemp = strTemp & strText
                    Else
                        strTemp = strTemp
                    End If
                End If
                '**********************************************
                rngImport.Offset(r, C) = strTemp
                
                C = C + 1
                strTemp = ""
            Else
                If strText <> Chr(34) Then strTemp = strTemp & strText
'                strTemp = strTemp & strText
            End If
        Next i
        C = 0
        r = r + 1
    Loop
    Close #1
    
    Msg = "외부자료를 다 읽어들였습니다." & vbCr & vbCr
    Msg = Msg & "입력자료를 생성합니다."
    MsgBox Msg, , "자료읽기"

    Call MakeInputFile
    Worksheets("ImportCSV").Delete
    
    Msg = "외부자료입력이 완료되었습니다." & vbCr & vbCr
    MsgBox Msg, , "입력완료"

End Sub
Function fnumImportMeasureNo() As Integer
   '****************************************
   ' 측정SET 개수
   '****************************************
    With Worksheets("ImportCSV")
        If .Range("B14") <> "" And .Range("B15") <> "" Then
            fnumImportMeasureNo = 2 '2번측정(1차 and 2차)
        Else
            fnumImportMeasureNo = 1 '1번측정(1차 or 2차)
        End If
    End With
End Function
Sub fnSaveTemp(frngSave As Worksheet, frngImport As Worksheet, j As Integer, fmLineNo As Variant)
    Dim mMeasureTime As String
   '*********************************************************************************************
   ' 현재 PDA의 문제점:처음에 측정방향을 REW로 잡고 측선을 1,2,3...인경우
   ' 출력시 아예 안바꾸어주던가 다바꾸어 주어야 하는데
   ' (이경우 측선번호는 바뀌어도 1,2,3...으로 표시해야함) REW-LEW는 바뀌지 않고
   ' 측선번호와 값만 바뀜. 따라서 일시적으로 아래와 같이 함(값은 LEW-REW형태로 출력이 되므로
   ' 측선번호와 LEW->REW만 고정함)
   '*********************************************************************************************
'   frngSave.Range("C8").Offset(0, 0) = frngImport.Range("C19").Offset(1, 0) 'LEW or REW
'   frngSave.Range("C59").Offset(0, 0) = frngImport.Range("C19").Offset(mLineNo, 0)  'LEW or REW
    frngSave.Range("C8").Offset(0, 0) = "LEW"
    frngSave.Range("C59").Offset(0, 0) = "REW"
    For i = 1 To fmLineNo
'       frngSave.Range("C8").Offset(i, 0) = frngImport.Range("C19").Offset(i + j, 1) '측선번호
        frngSave.Range("C8").Offset(i, 0) = i
        frngSave.Range("C8").Offset(i, 1) = frngImport.Range("C19").Offset(i + j, 2) '거리
        frngSave.Range("C8").Offset(i, 2) = frngImport.Range("C19").Offset(i + j, 3) '수심
        
        mMeasureTime = frngImport.Range("C19").Offset(i + j, 4) ' 시간표현변환 1200->12:00
        If mMeasureTime <> "" Then
            frngSave.Range("C8").Offset(i, 3) = Mid(mMeasureTime, 1, 2) & ":" & Mid(mMeasureTime, 3, 4) '시간
        End If
        frngSave.Range("C8").Offset(i, 4) = frngImport.Range("C19").Offset(i + j, 5) '수위
        
        frngSave.Range("I8").Offset(i, 0) = frngImport.Range("O19").Offset(i + j, 0) '각보정
        frngSave.Range("I8").Offset(i, 1) = frngImport.Range("O19").Offset(i + j, 1) '회전수
        frngSave.Range("I8").Offset(i, 2) = frngImport.Range("O19").Offset(i + j, 2) '측정시간
    
        frngSave.Range("I8").Offset(i, 4) = frngImport.Range("O19").Offset(i + j, 8)
        frngSave.Range("I8").Offset(i, 5) = frngImport.Range("O19").Offset(i + j, 9)
        frngSave.Range("I8").Offset(i, 6) = frngImport.Range("O19").Offset(i + j, 10)
            
'       050321수정
'        frngSave.Range("I8").Offset(i, 8) = frngImport.Range("O19").Offset(i + j, 13)
'        frngSave.Range("I8").Offset(i, 9) = frngImport.Range("O19").Offset(i + j, 14)
'        frngSave.Range("I8").Offset(i, 10) = frngImport.Range("O19").Offset(i + j, 15)
        frngSave.Range("I8").Offset(i, 8) = frngImport.Range("O19").Offset(i + j, 12)
        frngSave.Range("I8").Offset(i, 9) = frngImport.Range("O19").Offset(i + j, 13)
        frngSave.Range("I8").Offset(i, 10) = frngImport.Range("O19").Offset(i + j, 14)
    Next i
End Sub
Sub fLineValue(frngCell As Range, frngSave As Worksheet, fmLineNo As Variant)
   '**************************************************************************************************************
   ' 첫번째
    Worksheets("입력시트").Range("C8:S8").Offset(1, 0) = frngSave.Range("C8:S8").Offset(1, 0).Value
   '**************************************************************************************************************
    For j = 2 To fmLineNo
        frngCell.Offset(j, 0).EntireRow.Insert 'shift:=xlUp '현재 위치 아래 삽입
        For i = 0 To 16
            If i = 0 Then
                frngCell.Offset(j, i).Borders(xlEdgeLeft).LineStyle = xlContinuous
                frngCell.Offset(j, i).Borders(xlEdgeRight).LineStyle = xlDot
            
                frngCell.Offset(j, i).Borders(xlEdgeLeft).Weight = xlMedium
                frngCell.Offset(j, i).Borders(xlEdgeRight).Weight = xlHairline
            ElseIf i = 16 Then
                frngCell.Offset(j, i).Borders(xlEdgeLeft).LineStyle = xlDot
                frngCell.Offset(j, i).Borders(xlEdgeRight).LineStyle = xlContinuous
            
                frngCell.Offset(j, i).Borders(xlEdgeLeft).Weight = xlHairline
                frngCell.Offset(j, i).Borders(xlEdgeRight).Weight = xlMedium
            Else
                frngCell.Offset(j, i).Borders(xlEdgeLeft).LineStyle = xlDot
                frngCell.Offset(j, i).Borders(xlEdgeRight).LineStyle = xlDot
            
                frngCell.Offset(j, i).Borders(xlEdgeLeft).Weight = xlHairline
                frngCell.Offset(j, i).Borders(xlEdgeRight).Weight = xlHairline
            End If
            
                frngCell.Offset(j, i).Borders(xlEdgeBottom).LineStyle = xlDot
                frngCell.Offset(j, i).Borders(xlEdgeTop).LineStyle = xlDot
                            
                frngCell.Offset(j, i).Borders(xlEdgeBottom).Weight = xlHairline
                frngCell.Offset(j, i).Borders(xlEdgeTop).Weight = xlHairline
        Next i
        frngCell.Offset(j, 0) = j
       '**************************************************************************************************************
       ' 2번째 부터
        Worksheets("입력시트").Range("C8:S8").Offset(j, 0) = frngSave.Range("C8:S8").Offset(j, 0).Value
       '**************************************************************************************************************
    Next j
    
End Sub
Sub MakeInputFile()
    Dim mDMNo As String   'DM No.
    Dim mSiteCode  As String  '지점코드
    Dim mMeasureDate As String '측정일
    Dim mStreamName As String '하천명
    Dim mSiteName As String   '지점명
    Dim mMeasurePosition As String '측정위치
    Dim mWeather As String    '날씨
    Dim mWind As String   '바람
    Dim mMember As String '측정자
    Dim mEtc As String    '기타
    Dim mEqmType As String   '기기종류
    Dim mEqmTypeNo As String  '기기번호
    Dim mEstEqn1 As String    '검정식1
    Dim mEstEqn2 As String    '검정식2
    Dim mUnit As String   '단위
    Dim mEstRange As String   '검정범위
    Dim mEstDate As String    '검정일
    Dim mMeasureMethod As String   '측정방법
    
    Dim mMeasureNo As String   '측정회수
    Dim mLineNo As Variant '측선수
    
    Dim rngCell As Range
    Dim rngImport As Worksheet
    Dim rngExport As Worksheet
    Dim rngExportT As Worksheet
    Dim rngSave1 As Worksheet
    Dim rngSave2 As Worksheet
    
    Set rngCell = Worksheets("입력시트").Range("C8")
    Set rngImport = Worksheets("ImportCSV")
    Set rngExport = Worksheets("입력시트")
    Set rngExportT = Worksheets("종합")
    Set rngSave1 = Worksheets("입력저장1")
    Set rngSave2 = Worksheets("입력저장2")
    
    mMeasureNo = fnumImportMeasureNo()
        
    mLineNo = rngImport.Range("I14")
    mDMNo = rngImport.Range("E6")
    mSiteCode = rngImport.Range("D6")
    mMeasureDate = rngImport.Range("G6")
    mStreamName = rngImport.Range("B6")
    mSiteName = rngImport.Range("C6")
    mMeasurePositon = rngImport.Range("F6")
    mWeather = rngImport.Range("H6")
    mWind = rngImport.Range("I6")
    mMember = rngImport.Range("J6")
    mEtc = rngImport.Range("K6")
    mEqmType = rngImport.Range("B10")
    mEqmTypeNo = rngImport.Range("C10")
    mEstEqn1 = rngImport.Range("D10")
    mEstEqn2 = rngImport.Range("E10")
    mUnit = rngImport.Range("F10")
    mEstRange = rngImport.Range("G10")
    mEstDate = rngImport.Range("H10")
    mMeasureMethod = rngImport.Range("J10")
   '****************************************************
   ' 입력/저장시트 내용지움
   '****************************************************
    Call delParts '입력저장시트 내용지움
   '****************************************************
   ' 불러온값 저장
   '****************************************************
    If mMeasureNo = 1 Then  '1번측정(1차 or 2차)
        Call fnSaveTemp(rngSave1, rngImport, 0, mLineNo)    '1회 측정의 경우(1차 또는 2차 측정 중 1회) "입력저장1"에 저장됨
    ElseIf mMeasureNo = 2 Then  '2번측정(1차 and 2차)
        Call fnSaveTemp(rngSave1, rngImport, 1, mLineNo)    '2회 측정의 경우 1차, 2차 측정이 각각 "입력저장1"과 "입력저장2"에 저장됨
        Call fnSaveTemp(rngSave2, rngImport, (1 + mLineNo), mLineNo)
    End If
   '****************************************************
   ' 입력시트 지우기(초기화)
   '****************************************************
    Do While rngCell.Offset(2, 0) <> ""
        rngCell.Offset(2, 0).EntireRow.Delete Shift:=xlUp
    Loop
   '****************************************************
   ' 입력시트 초기화면(콤보상자)
   '****************************************************
    With Worksheets("입력시트")
        .CB_mNum = "M1"
        .CB_dir_start = Worksheets("입력저장1").Range("C8").Offset(0, 0)
        .CB_dir_end = Worksheets("입력저장1").Range("C8").Offset(51, 0)
    End With
   '****************************************************
   ' 입력시트 초기화면(값및양식채우기)
   '****************************************************
    Call fLineValue(rngCell.Offset(0, 0), rngSave1, mLineNo)
    
    With Worksheets("종합")
        .Range("N1") = mDMNo
        .Range("B4") = Mid(mMeasureDate, 1, 4) & "-" & Mid(mMeasureDate, 5, 2) & "-" & Mid(mMeasureDate, 7, 2)
        .Range("N2") = mStreamName
        .Range("N3") = mSiteName
        .Range("N4") = mMeasurePositon
        .Range("F4") = mWeather
        .Range("I4") = mWind
        .Range("C26") = mMember
        .Range("C27") = mEtc
       '*************************************************
       ' 유속계설정
       '*************************************************
        .Range("K21") = mEqmType
        .Range("K22") = mEqmTypeNo
        .Range("K23") = Worksheets("이름정의").Range("C16").Offset(fNoselMeter, 1)    '세밀한 표현을 위해서
        .Range("K24") = mEstRange
        .Range("K26") = mEstDate
    End With
End Sub
Sub msgBoxSelectionError()
    Dim Msg, Style, Title
    
    Msg = "유효한 삽입/삭제 위치를 선택해 주세요"    ' 메시지를 정의합니다.
    Style = vbOKOnly                     ' 단추를 정의합니다.
    Title = "선택영역오류!"    ' 제목을 정의합니다.
    
    MsgBox Msg, Style, Title ' 메시지 화면 표시
End Sub
Sub msgBoxDisOrderError()
    Dim Msg, Style, Title
    
    Msg = "측선거리를 정확히 입력하십시요!."    ' 메시지를 정의합니다.
    Style = vbOKOnly                     ' 단추를 정의합니다.
    Title = "측선거리입력 오류!"    ' 제목을 정의합니다.
    
    MsgBox Msg, Style, Title ' 메시지 화면 표시
End Sub
Sub InsertRows()
    Dim rngCell As Range
    Dim j, Count_Row
    Set rngCell = Range("C8")
    
Count_Row = InputBox("추가할 측선의 갯수")

If Len(Count_Row) = 0 Then

    End
    
End If
    
For j = 1 To Count_Row
    rN = ActiveCell.Row '현재 Row Number
    If rN < 9 Or Range("C1").Offset(rN - 1, 0) = "" Then
        Call msgBoxSelectionError
        Exit Sub
    Else
        intNo = Range("C1").Offset(rN - 1, 0) ' 현재 측선번호
        ActiveCell.Offset(1, 0).EntireRow.Insert Shift:=xlUp '현재 위치 아래 삽입
    
        intNo = intNo + 1
        rngCell.Offset(intNo, 0) = intNo '추가된 행의 측선번호
    
        For i = 0 To 16
            If i = 0 Then
                rngCell.Offset(intNo, i).Borders(xlEdgeLeft).LineStyle = xlContinuous
                rngCell.Offset(intNo, i).Borders(xlEdgeRight).LineStyle = xlDot
            
                rngCell.Offset(intNo, i).Borders(xlEdgeLeft).Weight = xlMedium
                rngCell.Offset(intNo, i).Borders(xlEdgeRight).Weight = xlHairline
            ElseIf i = 16 Then
                rngCell.Offset(intNo, i).Borders(xlEdgeLeft).LineStyle = xlDot
                rngCell.Offset(intNo, i).Borders(xlEdgeRight).LineStyle = xlContinuous
            
                rngCell.Offset(intNo, i).Borders(xlEdgeLeft).Weight = xlHairline
                rngCell.Offset(intNo, i).Borders(xlEdgeRight).Weight = xlMedium
            Else
                rngCell.Offset(intNo, i).Borders(xlEdgeLeft).LineStyle = xlDot
                rngCell.Offset(intNo, i).Borders(xlEdgeRight).LineStyle = xlDot
            
                rngCell.Offset(intNo, i).Borders(xlEdgeLeft).Weight = xlHairline
                rngCell.Offset(intNo, i).Borders(xlEdgeRight).Weight = xlHairline
            End If
            
                rngCell.Offset(intNo, i).Borders(xlEdgeBottom).LineStyle = xlDot
                rngCell.Offset(intNo, i).Borders(xlEdgeTop).LineStyle = xlDot
        
                rngCell.Offset(intNo, i).Borders(xlEdgeBottom).Weight = xlHairline
                rngCell.Offset(intNo, i).Borders(xlEdgeTop).Weight = xlHairline
        Next i
    
        Do While rngCell.Offset(intNo + 1, 0) <> ""
            intNo = intNo + 1
'           rngCell.Offset(intNo, 0) = intNo '이하 측선번호 1씩 증가
            rngCell.Offset(intNo, 0) = rngCell.Offset(intNo, 0) + 1
        Loop
    End If

Next j
End Sub
Sub DelRows()
    Dim rngCell As Range
    Set rngCell = Range("C8")
    Dim j, Count_Row
    
Count_Row = InputBox("삭제할 측선의 갯수")
    
If Len(Count_Row) = 0 Then

    End
    
End If
    
For j = 1 To Count_Row

    rN = ActiveCell.Row '현재 Row Number
    If rN < 9 Or Range("C1").Offset(rN - 1, 0) = "" Or Application.Count(Range("C9:C65536")) = 1 Then
        Call msgBoxSelectionError
        Exit Sub
    Else
        intNo = Range("C1").Offset(rN - 1, 0) ' 현재 측선번호
    
        ActiveCell.EntireRow.Delete Shift:=xlUp
    
        For i = 0 To 16
'           rngCell.Offset(intNo, i).Borders(xlEdgeBottom).LineStyle = xlDot
            rngCell.Offset(intNo, i).Borders(xlEdgeTop).LineStyle = xlDot
        
'           rngCell.Offset(intNo, i).Borders(xlEdgeBottom).Weight = xlHairline
            rngCell.Offset(intNo, i).Borders(xlEdgeTop).Weight = xlHairline
        Next i
  
        Do While rngCell.Offset(intNo, 0) <> ""
            rngCell.Offset(intNo, 0) = rngCell.Offset(intNo, 0) - 1 '이하 측선번호 1씩 감소
            intNo = intNo + 1
        Loop
    End If
Next j
End Sub
Sub delInput()
    Dim rngCell As Range
    Dim intNo As Integer
    Dim myBtn As Integer
    Dim myMsg As String
    Dim myTitle As String
    
    myMsg = "재측정을 하시겠습니까?" & Chr(13) & "현재 측정된 데이터가 삭제됩니다."
    myTitle = "재측정 확인"
    
    myBtn = MsgBox(myMsg, vbYesNo + vbExclamation, myTitle)
    
    
    
    If myBtn = vbYes Then
        Set rngCell = Worksheets("입력시트").Range("C8")
    
        intNo = 1
        Do While rngCell.Offset(intNo, 0) <> ""
            For i = 1 To 18
                rngCell.Offset(intNo, i).ClearContents
            Next i
            intNo = intNo + 1
        Loop
    End If
    
    Range("D9").Select
    
    'Range(Sheets("입력시트").Cells(1, 246), Sheets("입력시트").Cells(10, 250)).ClearContents
    'Sheets("이름정의").Range("G11").ClearContents
End Sub
Sub dellAll()
    Dim rngCell As Range
    Dim intNo As Integer
    Dim myBtn As Integer
    Dim myMsg As String
    Dim myTitle As String
    Dim FName As Variant
    
    myMsg = "새측정을 하시겠습니까?"
    myTitle = "새측정 확인"
    
    myBtn = MsgBox(myMsg, vbYesNo + vbExclamation, myTitle)
    
    If myBtn = vbYes Then
                        
        Range(Sheets("입력시트").Cells(1, 246), Sheets("입력시트").Cells(10, 250)).ClearContents
                        
        ActiveWorkbook.Save '현재 문서저장
       '**************************************
       '    새문서 이름 입력 저장
       '**************************************
        FName = Application.GetSaveAsFilename(fileFilter:="Excel Files (*.xls), *.xls")

        If FName <> False Then
            ActiveWorkbook.SaveAs Filename:=FName, CreateBackup:=True
        End If
       '**************************************
        
        Call delAllS
        Sheets("이름정의").Range("G11").ClearContents
    End If
End Sub
Sub SetIniDir()
    '**************************************
    '    초기 방향설정
    '**************************************
    With Worksheets("입력시트")
        .CB_mNum = "M1"
        .CB_dir_start = "LEW"
        .CB_dir_end = "REW"
    End With
End Sub
Sub delAllS()
    Set rngCell = Worksheets("입력시트").Range("C8")
    intNo = 1
    Do While rngCell.Offset(intNo, 0) <> ""
        For i = 1 To 18
            rngCell.Offset(intNo, i).ClearContents
        Next i
        intNo = intNo + 1
    Loop
    
    Call delParts
    Call SetIniDir
    
End Sub
Sub delParts()
    Worksheets("계산1").Range("B9:AC108").ClearContents
    Worksheets("계산2").Range("B9:AC108").ClearContents
   '**************************************
   '    평균수위계산 항목 지우기
   '**************************************
    Worksheets("계산1").Range("AC9:AC114").ClearContents
    Worksheets("계산2").Range("AC9:AC114").ClearContents
    Worksheets("불확실도1").Range("B9:AA114").ClearContents
    Worksheets("불확실도2").Range("B9:AA114").ClearContents
    Worksheets("입력저장1").Range("C8:U109").ClearContents
    Worksheets("입력저장2").Range("C8:U109").ClearContents
    Worksheets("입력저장1").Range("C8:U109").Interior.ColorIndex = xlNone
    Worksheets("입력저장2").Range("C8:U109").Interior.ColorIndex = xlNone
        
        
   '**************************************
   '    종합시트 항목 지우기
   '**************************************
    With Worksheets("종합")
        .Range("B4:D4").ClearContents     '측정일
        .Range("F4").ClearContents        '날씨
        .Range("I4:J4").ClearContents     '바람
        
        .Range("N1:S4").ClearContents     'DM, 하천, 지점, 측정위치
        .Range("C7:G22").ClearContents    '수위
        .Range("K7:S13").ClearContents    '수질
        .Range("K15:S19").ClearContents   '시료
        .Range("K21:S27").ClearContents   '유속계
           
        .Range("C26:G27").ClearContents   '측정자, 비고
    End With
End Sub
Sub calDepth()
    Dim rngCell As Range
    Dim rDepth As Variant
    
    Set rngCell = Range("C8")
    
    intNo = 1
    Do While rngCell.Offset(intNo, 0) <> ""
    
        rDepth = rngCell.Offset(intNo, 2)
        
        If rDepth = "" Then
            rngCell.Offset(intNo, 5) = ""
            rngCell.Offset(intNo, 9) = ""
            rngCell.Offset(intNo, 13) = ""
        Else
            Select Case rDepth
                Case Is < 0.6
                    rngCell.Offset(intNo, 5) = ""
                    rngCell.Offset(intNo, 9) = rDepth * 0.4
                    rngCell.Offset(intNo, 13) = ""
                Case Is < 1#
                    rngCell.Offset(intNo, 5) = rDepth * 0.8
                    rngCell.Offset(intNo, 9) = ""
                    rngCell.Offset(intNo, 13) = rDepth * 0.2
                Case Is >= 1#
                    rngCell.Offset(intNo, 5) = rDepth * 0.8
                    rngCell.Offset(intNo, 9) = rDepth * 0.4
                    rngCell.Offset(intNo, 13) = rDepth * 0.2
            End Select
        End If
        intNo = intNo + 1
    Loop

End Sub
Sub mainCalFlow()
   '***********************************************
   '    입력값저장
   '***********************************************
    
    '*********************************************
    '각시트별 자료 초기화 20131128 이기성 수정
    '*********************************************
    
        Select Case Worksheets("이름정의").Range("D11")
        Case "M1"
            Worksheets("입력저장1").Range("C8:S109").ClearContents
            Worksheets("계산1").Range("B9:AD108").ClearContents
            Worksheets("계산1").Range("AC114").ClearContents
            Worksheets("불확실도1").Range("B9:AD114").ClearContents
            'If Application.CountA(Range(Sheets("입력저장1").Cells(9, 20), Sheets("입력저장1").Cells(108, 20))) = 0 Then
                'Call SaveInp
            'End If
        Case "M2"
            Worksheets("입력저장2").Range("C8:S109").ClearContents
            Worksheets("계산2").Range("B9:AD108").ClearContents
            Worksheets("계산2").Range("AC114").ClearContents
            Worksheets("불확실도2").Range("B9:AD114").ClearContents
            'If Application.CountA(Range(Sheets("입력저장2").Cells(9, 20), Sheets("입력저장2").Cells(108, 20))) = 0 Then
                'Call SaveInp
            'End If
            
    End Select
        
        Call SaveInp
        
        If InStr(Sheets("종합").Cells(22, 11), Chr(10)) <> 0 Then
            
            유속계입력
                
        Else
        
            Select Case Worksheets("이름정의").Range("D11")
                Case "M1"
                Worksheets("입력저장1").Range("T9").Resize(Application.Count(Range(Sheets("입력시트").Cells(9, 3), Sheets("입력시트").Cells(65536, 3)))) = Sheets("종합").Range("K22")
                Worksheets("입력저장1").Columns("T:T").EntireColumn.AutoFit

            Case "M2"
                Worksheets("입력저장2").Range("T9").Resize(Application.Count(Range(Sheets("입력시트").Cells(9, 3), Sheets("입력시트").Cells(65536, 3)))) = Sheets("종합").Range("K22")
                Worksheets("입력저장2").Columns("T:T").EntireColumn.AutoFit
            End Select
                
            
        End If
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ufSelCal.Left = 100 '2013.12.05 이기성 수정
    ufSelCal.Show

    '****************************************************************
    '   차트그리기
    '****************************************************************
    Call chartM
    Call ChartOnUserform
    'End
End Sub
Sub calFlow(rTimes As Integer)
'***********************************************
'   유량 및 불확실도 계산
'***********************************************
'   변수 선언
'***********************************************
    Dim rngCell As Range
'    Dim rngOcell As Range
    
    Dim calD As Integer
    
    Dim rLength(100, 3) As Double
    Dim rDepth(100, 3) As Double
    
    Dim rLtime(100, 3) As Variant
    Dim rLdepth(100, 3) As Variant
    Dim rLpow(100, 3) As Double
    Dim rLPsum As Double
    Dim rLDsum As Double
    Dim rLmax As Double
    Dim rLmin As Double
    Dim rLsum As Double
    Dim rLnum As Double
    Dim rLave As Double
'    Dim rTimes As Integer
    Dim rIndxBlank As Double
    Dim rPowBlank As Double
    
    Dim rWidth(100, 3) As Double
    Dim rmVel(100, 3) As Double
    
    Dim rArea(100, 3) As Double
    Dim rDis(100, 3) As Double
    Dim rRad(100, 3) As Variant
    
    Dim rRev2(100, 3) As Double
    Dim rRev6(100, 3) As Double
    Dim rRev8(100, 3) As Double
    
    Dim rVel2(100, 3) As Double
    Dim rVel6(100, 3) As Double
    Dim rVel8(100, 3) As Double
    
    Dim raVel2(100, 3) As Double
    Dim raVel6(100, 3) As Double
    Dim raVel8(100, 3) As Double
   
    Dim rA2(100, 3) As Double
    Dim rA6(100, 3) As Double
    Dim rA8(100, 3) As Double
    
    Dim rR2(100, 3) As Double
    Dim rR6(100, 3) As Double
    Dim rR8(100, 3) As Double
    
    Dim rNpoint(100, 3) As Integer
        
    Dim rT2(100, 3) As Double
    Dim rT6(100, 3) As Double
    Dim rT8(100, 3) As Double
    
    Dim rBlank2(100, 3) As Integer
    Dim rBlank6(100, 3) As Integer
    Dim rBlank8(100, 3) As Integer
    
    Dim rw1 As Double
    Dim rw2 As Double
    Dim rmT As Double
    Dim rdbv As Double
    Dim sdbv As Double
    
    Dim rdbv2 As Double
    Dim rXb As Double
    Dim rXd As Double
    Dim rXe As Double
    Dim rXp As Double
    Dim rXc As Double
    Dim rXm As Double
    Dim rSigma As Double
    Dim sSigma As Double
    Dim XpQ As Double
    
    Dim Xppb As Double
    Dim Xppd As Double
    Dim Xppc As Double
    Dim XppQ As Double
    
    Dim XQ As Double
    
    Dim cXb As Double
    Dim cXd As Double
    Dim cXe As Double
    Dim cXp As Double
    Dim cXc As Double
    
    Dim scXb As Double
    Dim scXd As Double
    Dim scXe As Double
    Dim scXp As Double
    Dim scXc As Double
    
    Dim scmpXm As Double
    Dim scmpXb As Double
    Dim scmpXd As Double
    Dim scmpXe As Double
    Dim scmpXp As Double
    Dim scmpXc As Double
    Dim sumCmp As Double
    
    Dim suniXm As Double
    Dim suniXb As Double
    Dim suniXd As Double
    Dim suniXe As Double
    Dim suniXp As Double
    Dim suniXc As Double
    Dim sumUni As Double
   '***********************************************
   '    첫,끝측선에 수심이 있는 경우 유속산정
   '    (Rantz, 1982, USGS)
   '    MMF 모델에 Fitting 한 Parameters
   '***********************************************
    Dim paA As Double
    Dim paB As Double
    Dim paC As Double
    Dim paD As Double
    Dim coX As Double
    Dim coY As Double
   '***********************************************
    
    Dim maxNo As Integer
    Dim i As Integer

    Dim outCell As Range
    Dim uncCell As Range

    Dim selMeter As Range
    Dim selMeterNo As Range
    Dim NoselMeter As Integer
'    Set selMeter = Worksheets("종합").Range("K21")
    Set selMeter = Worksheets("이름정의").Range("G11")
    Set selMeterNo = Worksheets("종합").Range("K22")
   '***********************************************
   ' Set rngCell = Range("C8")
   '***********************************************
   '    Input/Output
   '***********************************************
    Select Case rTimes
        Case 1  '1번측정한 경우(1차, 2차 구분없음)
            Set rngCell = Worksheets("입력저장1").Range("C8")
            Set outCell = Worksheets("계산1").Range("A8")
            Set uncCell = Worksheets("불확실도1").Range("B8")
            Set allstCell = Worksheets("종합").Range("C8")
            Set alledCell = Worksheets("종합").Range("C13")
        Case 2  '2번측정한 경우(2번째 측정한 값 계산 및 저장)
            Set rngCell = Worksheets("입력저장2").Range("C8")
            Set outCell = Worksheets("계산2").Range("A8")
            Set uncCell = Worksheets("불확실도2").Range("B8")
            Set allstCell = Worksheets("종합").Range("C16")
            Set alledCell = Worksheets("종합").Range("C21")
        Case Else
                MsgBox "Errror"
    End Select
   '***********************************************
   ' NoselMeter = fNoselMeter() ' 유속계 2개 이상 사용을 위해 비활성화 2013.11.29 이기성 수정
   '***********************************************
   '    측정회차, 최대측선수, 측정방향 설정
 '   rTimes = selMeasure()
    maxNo = calmaxNo(rngCell)
   '***********************************************
   '    측정방향 인식(2004/07/12 수정)
   '    각 회차별로 달리 인식가능
   '***********************************************
 '   calD = calDir()
    calD = calDir(rTimes)
   '***********************************************
   '    평균수위(초기화)
   '***********************************************
    rLmax = 0
    rLmin = 10000
    rLnum = 0
    rLsum = 0
    rLDsum = 0
    rLPsum = 0
    rIndxBlank = 1
    rPowBlank = 1
   '***********************************************
   '    첫측선 끝측선에 수심이 있을경우 유속계산
   '    (MMF Model Fitting)
   '***********************************************
    paA = 0.65
    paB = 0.71428386
    paC = 1.2499993
    paD = 0.48542614
   '***********************************************
   '    입력
   '***********************************************
    For i = 1 To maxNo
        ic = caldirNo(calD, maxNo, i)
        
       '******************************************
       '    거리, 수심 입력
       '******************************************
        rLength(ic, rTimes) = rngCell.Offset(i, 1)
        rDepth(ic, rTimes) = rngCell.Offset(i, 2)
       '******************************************
       '    각보정계수 입력
       '******************************************
        rA2(ic, rTimes) = rngCell.Offset(i, 6)
        rA6(ic, rTimes) = rngCell.Offset(i, 10)
        rA8(ic, rTimes) = rngCell.Offset(i, 14)
       '******************************************
       '    회전수 입력
       '******************************************
        rR2(ic, rTimes) = rngCell.Offset(i, 7)
        rR6(ic, rTimes) = rngCell.Offset(i, 11)
        rR8(ic, rTimes) = rngCell.Offset(i, 15)
        
        If rngCell.Offset(i, 7) = "" Then
            rBlank2(ic, rTimes) = 0
        Else
            rBlank2(ic, rTimes) = 1
        End If
        
        If rngCell.Offset(i, 11) = "" Then
            rBlank6(ic, rTimes) = 0
        Else
            rBlank6(ic, rTimes) = 1
        End If
        
        If rngCell.Offset(i, 15) = "" Then
            rBlank8(ic, rTimes) = 0
        Else
            rBlank8(ic, rTimes) = 1
        End If
       '******************************************
       '    1,2,3점법 결정
       '******************************************
        rNpoint(ic, rTimes) = fNpoint(rngCell.Offset(i, 7), rngCell.Offset(i, 11), rngCell.Offset(i, 15))
       '******************************************
       '    측정시간 입력
       '******************************************
        rT2(ic, rTimes) = rngCell.Offset(i, 8)
        rT6(ic, rTimes) = rngCell.Offset(i, 12)
        rT8(ic, rTimes) = rngCell.Offset(i, 16)
       
       '******************************************
       '    하폭계산
       '******************************************
            If i = 1 Then
                rw1 = rngCell.Offset(i, 1)
                rw2 = rngCell.Offset(i + 1, 1)
            ElseIf i = maxNo Then
                rw1 = rngCell.Offset(i - 1, 1)
                rw2 = rngCell.Offset(i, 1)
            Else
                rw1 = rngCell.Offset(i - 1, 1)
                rw2 = rngCell.Offset(i + 1, 1)
            End If
            rWidth(ic, rTimes) = fnWidth(rw1, rw2)
       '******************************************
       '평균수위 계산용(각 측선별 시각과 수위)
       '******************************************
        rLtime(ic, rTimes) = rngCell.Offset(i, 3)
        rLdepth(ic, rTimes) = rngCell.Offset(i, 4)
        
        rIndxBlank = fIndxBlank(rLdepth(ic, rTimes))
        rPowBlank = rPowBlank * rIndxBlank
    Next i
   '******************************************
   '    입력 끝
   '******************************************
   
   '******************************************
   '    계산과정
   '******************************************
    
   '***********************************************
    '유속계 2개 이상 사용을 위한 코드수정 2013.11.29 이기성 수정
    Dim 유속계 As Variant
    Dim 평균, P_i, P_j, P_k
    
    If InStr(Sheets("종합").Cells(22, 11), Chr(10)) <> 0 Then
        
        P_j = Application.CountA(Sheets("입력시트").Range("IM1:IM10"))
        
        유속계 = Range(Sheets("입력시트").Cells(1, 247), Sheets("입력시트").Cells(P_j, 248))
        
    Else
    
        ReDim 유속계(1, 1)
        
        유속계(1, 1) = selMeterNo
        
        P_j = 1
        
    End If
    
    'tex = selMeterNo
    
    
    'P_i = 1
    
    'Do
    
        'P_i = P_i + 1
        
        'tex = Right(tex, Len(tex) - InStr(tex, Chr(10)))
    
    'Loop Until InStr(tex, Chr(10)) = 0
    
    
    'ReDim 유속계(P_i + 1, 2)
    
    'P_j = 0
    
    'tex = selMeterNo
    'Do
    
        'P_j = P_j + 1
        
        'If InStr(tex, Chr(10)) <> 0 Then
            '유속계(P_j, 1) = Left(tex, InStr(tex, Chr(10)) - 1)
            
            'If P_j <> 1 Then
                '유속계(P_j, 2) = P_j
            'End If
        'Else
        
            '유속계(P_j, 1) = tex
            '유속계(P_j, 2) = P_j
        
        'End If
        
        'tex = Right(tex, Len(tex) - InStr(tex, Chr(10)))
    
    'Loop Until P_i = P_j
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    For i = 1 To maxNo
    
   '***********************************************
    '유속계 2개 이상 사용을 위한 코드수정 2013.11.29 이기성 수정
    For P_i = 1 To P_j
        
        ic = caldirNo(calD, maxNo, i)
        
        'If Len(rngCell.Offset(ic, 17)) <> 0 Then
        'If Len(Sheets("입력시트").Cells(i + 8, 21)) <> 0 Then
            'P_k = rngCell.Offset(ic, 17)
            If rngCell.Offset(ic, 17) = 유속계(P_i, 1) Then
                selMeterPara = 유속계(P_i, 1)
                Exit For
            End If
        'Else
            'selMeterPara = 유속계(1, 1)
            'Exit For
        'End If
    Next P_i
    
    
    
    NoselMeter = fNoselMeter()
   '***********************************************
    
        If (i = 1 Or i = maxNo) Then
            rRev2(i, rTimes) = 0
            rRev6(i, rTimes) = 0
            rRev8(i, rTimes) = 0
            
            rVel2(i, rTimes) = 0
            rVel6(i, rTimes) = 0
            rVel8(i, rTimes) = 0
            
            raVel2(i, rTimes) = 0
            raVel6(i, rTimes) = 0
            raVel8(i, rTimes) = 0
            
        Else
           '*****************************************
           '   초당 회전수 계산
           '*****************************************
'            If selMeter = "유속입력" Then
            '********************************
            '유속계 2개 사용에 따른 코드 수정 2013.12.02 이기성 수정
            '********************************
            
            If InStr(Sheets("종합").Cells(22, 11), Chr(10)) <> 0 Then '기본입력.CheckBox1.Visible = True Then
                
                selMeter = 유속계(P_i, 2)
                
                'If InStr(rngCell.Offset(ic, 7), ".") Or InStr(rngCell.Offset(ic, 11), ".") Or InStr(rngCell.Offset(ic, 15), ".") Then
                    'selMeter = "유속"
                'Else
                    'selMeter = "회전수"
                'End If
            End If
            '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            
            If selMeter = "유속" Then
                rRev2(i, rTimes) = fnRev(rR2(i, rTimes), 1#)     '0.2D
                rRev6(i, rTimes) = fnRev(rR6(i, rTimes), 1#)      '0.6D
                rRev8(i, rTimes) = fnRev(rR8(i, rTimes), 1#)      '0.8D
            Else
                rRev2(i, rTimes) = fnRev(rR2(i, rTimes), rT2(i, rTimes))    '0.2D
                rRev6(i, rTimes) = fnRev(rR6(i, rTimes), rT6(i, rTimes))    '0.6D
                rRev8(i, rTimes) = fnRev(rR8(i, rTimes), rT8(i, rTimes))    '0.8D
            End If
           '*****************************************
           '   측점별 유속 계산
           '*****************************************
            Select Case rNpoint(i, rTimes)
                Case 1
                    rVel2(i, rTimes) = 0  '0.2D
                    rVel6(i, rTimes) = fnaveVel(NoselMeter, selMeter, selMeterNo, rR6(i, rTimes), rRev6(i, rTimes)) '0.6D
                    rVel8(i, rTimes) = 0  '0.8D
                Case 2
                    rVel2(i, rTimes) = fnaveVel(NoselMeter, selMeter, selMeterNo, rR2(i, rTimes), rRev2(i, rTimes)) '0.2D
                    rVel6(i, rTimes) = 0  '0.6D
                    rVel8(i, rTimes) = fnaveVel(NoselMeter, selMeter, selMeterNo, rR8(i, rTimes), rRev8(i, rTimes)) '0.8D
                Case 3
                    rVel2(i, rTimes) = fnaveVel(NoselMeter, selMeter, selMeterNo, rR2(i, rTimes), rRev2(i, rTimes)) '0.2D
                    rVel6(i, rTimes) = fnaveVel(NoselMeter, selMeter, selMeterNo, rR6(i, rTimes), rRev6(i, rTimes)) '0.6D
                    rVel8(i, rTimes) = fnaveVel(NoselMeter, selMeter, selMeterNo, rR8(i, rTimes), rRev8(i, rTimes)) '0.8D
            End Select
           '*****************************************
           '   측점별 유속 계산(각보정)
           '*****************************************
            raVel2(i, rTimes) = rA2(i, rTimes) * rVel2(i, rTimes) '0.2D
            raVel6(i, rTimes) = rA6(i, rTimes) * rVel6(i, rTimes) '0.6D
            raVel8(i, rTimes) = rA8(i, rTimes) * rVel8(i, rTimes) '0.8D
        End If
       '*****************************************
       '   측선별 평균유속 계산
       '*****************************************
        'rmVel(i, rTimes) = fmVel(raVel2(i, rTimes), raVel6(i, rTimes), raVel8(i, rTimes))
        rmVel(i, rTimes) = fmVel(raVel2(i, rTimes), raVel6(i, rTimes), raVel8(i, rTimes), rNpoint(i, rTimes)) '유속에 관계없이 점법으로 계산'2014-01-06 이기성 수정
'       *****************************************
       '*****************************************
       '   측선별 면적, 유량 계산
       '*****************************************
        rArea(i, rTimes) = rWidth(i, rTimes) * rDepth(i, rTimes)
        rDis(i, rTimes) = rArea(i, rTimes) * rmVel(i, rTimes)
       '*****************************************
       '   윤변 계산
       '*****************************************
        If i = 1 Then
           '*****************************************
           '   윤변 첫 측선
           '*****************************************
            If rDepth(i, rTimes) = 0 Then
                rRad(i, rTimes) = ""
            Else
                rRad(i, rTimes) = rDepth(i, rTimes)
            End If
        Else
            rRad(i, rTimes) = ((rLength(i, rTimes) - rLength(i - 1, rTimes)) ^ 2 + (rDepth(i, rTimes) - rDepth(i - 1, rTimes)) ^ 2) ^ 0.5
        End If
        
       '******************************************
       '평균수위 계산
       '*****************************************
        If rLdepth(i, rTimes) <> "" And rLdepth(i, rTimes) > rLmax Then
            rLmax = rLdepth(i, rTimes)
        End If
        
        If rLdepth(i, rTimes) <> "" And rLdepth(i, rTimes) < rLmin Then
            rLmin = rLdepth(i, rTimes)
        End If
        
        If rLdepth(i, rTimes) <> "" Then
            rLnum = rLnum + 1
            rLsum = rLsum + rLdepth(i, rTimes)
        End If
        rLpow(i, rTimes) = rDis(i, rTimes) * rLdepth(i, rTimes)
        rLDsum = rLDsum + rDis(i, rTimes)  '유량 합
        rLPsum = rLPsum + rLpow(i, rTimes) '유량*수위 합
  '****************************************************
  '   2004-01-12 수정됨(For Next 분리)
  '****************************************************
   Next i
  '****************************************************
   For i = 1 To maxNo
  '****************************************************
       '***********************************************
       '    첫,끝측선에 수심이 있는경우 유속,유량재계산
       '    수심이 있으면(rDepth>0) 재계산
       '    Rantz 공식을 MMF모델에 Fittting
       '***********************************************
        If i = 1 Then
            If rDepth(i, rTimes) > 0 Then
                coX = 2 * rWidth(i, rTimes) / rDepth(i, rTimes)
                coY = (paA * paB + paC * coX ^ paD) / (paB + coX ^ paD)
                rmVel(i, rTimes) = (0.65 / coY) * rmVel(i + 1, rTimes)
                rDis(i, rTimes) = rArea(i, rTimes) * rmVel(i, rTimes)
            End If
        End If
        If i = maxNo Then
            If rDepth(i, rTimes) > 0 Then
                coX = 2 * rWidth(i, rTimes) / rDepth(i, rTimes)
                coY = (paA * paB + paC * coX ^ paD) / (paB + coX ^ paD)
                rmVel(i, rTimes) = (0.65 / coY) * rmVel(i - 1, rTimes)
                rDis(i, rTimes) = rArea(i, rTimes) * rmVel(i, rTimes)
            End If
        End If
       '***********************************************
       '    유량계산 결과
       '*****************************************
        outCell.Offset(i, 1) = i
        outCell.Offset(i, 2) = rLength(i, rTimes)
        outCell.Offset(i, 3) = rWidth(i, rTimes)
        outCell.Offset(i, 4) = rDepth(i, rTimes)
            
        If rBlank2(i, rTimes) = 1 Then
            outCell.Offset(i, 5) = rA2(i, rTimes)
            outCell.Offset(i, 6) = rR2(i, rTimes)
            outCell.Offset(i, 7) = rT2(i, rTimes)
            outCell.Offset(i, 8) = frRev(selMeter, rRev2(i, rTimes))
            outCell.Offset(i, 17) = rVel2(i, rTimes)
            outCell.Offset(i, 20) = raVel2(i, rTimes)
        
        ElseIf rBlank2(i, rTimes) = 0 Then
            outCell.Offset(i, 5) = ""
            outCell.Offset(i, 6) = ""
            outCell.Offset(i, 7) = ""
            outCell.Offset(i, 8) = ""
            outCell.Offset(i, 17) = ""
            outCell.Offset(i, 20) = ""
        End If
            
        If rBlank6(i, rTimes) = 1 Then
            outCell.Offset(i, 9) = rA6(i, rTimes)
            outCell.Offset(i, 10) = rR6(i, rTimes)
            outCell.Offset(i, 11) = rT6(i, rTimes)
            '********************************
            '유속계 2개 사용에 따른 코드 수정 2013.12.02 이기성 수정
            '********************************
            ic = caldirNo(calD, maxNo, i)
            If InStr(Sheets("종합").Cells(22, 11), Chr(10)) Then '기본입력.CheckBox1.Visible = True Then
            
                If InStr(rngCell.Offset(ic, 7), ".") Or InStr(rngCell.Offset(ic, 11), ".") Or InStr(rngCell.Offset(ic, 15), ".") Then
                
                    selMeter = "유속"
                    
                Else
                
                    selMeter = "회전수"
                    
                End If
                
            End If
            ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            
            outCell.Offset(i, 12) = frRev(selMeter, rRev6(i, rTimes))
            outCell.Offset(i, 18) = rVel6(i, rTimes)
            outCell.Offset(i, 21) = raVel6(i, rTimes)
        ElseIf rBlank6(i, rTimes) = 0 Then
            outCell.Offset(i, 9) = ""
            outCell.Offset(i, 10) = ""
            outCell.Offset(i, 11) = ""
            outCell.Offset(i, 12) = ""
            outCell.Offset(i, 18) = ""
            outCell.Offset(i, 21) = ""
        End If
        
        If rBlank8(i, rTimes) = 1 Then
            outCell.Offset(i, 13) = rA8(i, rTimes)
            outCell.Offset(i, 14) = rR8(i, rTimes)
            outCell.Offset(i, 15) = rT8(i, rTimes)
            outCell.Offset(i, 16) = frRev(selMeter, rRev8(i, rTimes))
            outCell.Offset(i, 19) = rVel8(i, rTimes)
            outCell.Offset(i, 22) = raVel8(i, rTimes)
        ElseIf rBlank8(i, rTimes) = 0 Then
            outCell.Offset(i, 13) = ""
            outCell.Offset(i, 14) = ""
            outCell.Offset(i, 15) = ""
            outCell.Offset(i, 16) = ""
            outCell.Offset(i, 19) = ""
            outCell.Offset(i, 22) = ""
        End If
            
        outCell.Offset(i, 23) = rmVel(i, rTimes)
                   
        outCell.Offset(i, 24) = rArea(i, rTimes)
        outCell.Offset(i, 25) = rDis(i, rTimes)
            
        outCell.Offset(i, 26) = rRad(i, rTimes)
       '*****************************************
       '    처음과 끝 측선
       '*****************************************
        If i = 1 Or i = maxNo Then
           '*************************************
           '    2004-01-09 수정됨
           '    For j = 5 To 25
           '    첫,끝측선에 수심이 있는경우 고려
           '    (Rantz,1982,USGS)
           '*************************************
            For j = 5 To 22     '23,24,25번열은 평균유속, 단면적 및 유량
                outCell.Offset(i, j) = ""
                outCell.Offset(maxNo, j) = ""
            Next j
        End If
       '**************************************
       '    윤변 끝 측선
       '*****************************************
        If i = maxNo Then
            If rDepth(i, rTimes) = 0 Then
                rRad(i, rTimes) = ""
            Else
                rRad(i + 1, rTimes) = rDepth(i, rTimes)
            End If
            outCell.Offset(i + 1, 26) = rRad(i + 1, rTimes)
        End If
                   
       '***********************************************
       '    불확실도 계산결과
       '*****************************************
        uncCell.Offset(i, 0) = i
        If i = 1 Or i = maxNo Then
            For j = 1 To 11
                uncCell.Offset(i, j) = ""
            Next j
        Else
            Select Case rNpoint(i, rTimes)
                Case Is = 1
                    uncCell.Offset(i, 1) = "1점법"
                Case Is = 2
                    uncCell.Offset(i, 1) = "2점법"
                Case Is = 3
                    uncCell.Offset(i, 1) = "3점법"
            End Select
                
            rmT = (rT2(i, rTimes) + rT6(i, rTimes) + rT8(i, rTimes)) / rNpoint(i, rTimes) / 60#
            uncCell.Offset(i, 2) = rmT
            uncCell.Offset(i, 3) = rmVel(i, rTimes)
                
            rdbv = rDepth(i, rTimes) * rWidth(i, rTimes) * rmVel(i, rTimes)
            sdbv = sdbv + rdbv
                
            rdbv2 = rdbv ^ 2
            rXb = 0.1
            rXd = 1#
            rXe = Xe_Error(rNpoint(i, rTimes), rmT, rmVel(i, rTimes))
            rXp = Xp_Error(rNpoint(i, rTimes))
            rXc = Xc_Error(rmVel(i, rTimes))
            rSigma = Sigma_Error(rdbv2, rXb, rXd, rXe, rXp, rXc)
            sSigma = sSigma + rSigma
                
            uncCell.Offset(i, 4) = rdbv
            uncCell.Offset(i, 5) = rdbv2
            uncCell.Offset(i, 6) = rXb
            uncCell.Offset(i, 7) = rXd
            uncCell.Offset(i, 8) = rXe
            uncCell.Offset(i, 9) = rXp
            uncCell.Offset(i, 10) = rXc
                
            uncCell.Offset(i, 11) = rSigma
           
            cXb = rdbv2 * rXb ^ 2
            cXd = rdbv2 * rXd ^ 2
            cXe = rdbv2 * rXe ^ 2
            cXp = rdbv2 * rXp ^ 2
            cXc = rdbv2 * rXc ^ 2
            scXb = scXb + cXb
            scXd = scXd + cXd
            scXe = scXe + cXe
            scXp = scXp + cXp
            scXc = scXc + cXc
                
            uncCell.Offset(i, 20) = cXb
            uncCell.Offset(i, 21) = cXd
            uncCell.Offset(i, 22) = cXe
            uncCell.Offset(i, 23) = cXp
            uncCell.Offset(i, 24) = cXc
        End If
       '*****************************************
       '    평균수위
       '*****************************************
        If rLdepth(i, rTimes) = "" Then
            outCell.Offset(i, 28) = ""
        Else
            outCell.Offset(i, 28) = rLpow(i, rTimes)
        End If
    Next i
   '*****************************************
    
   '*****************************************
   '    총불확실도 및 불확실도 상대비중 계산
   '*****************************************
    rXm = Xm_Error(maxNo)
    XpQ = (rXm ^ 2 + (sSigma / sdbv ^ 2)) ^ 0.5
    
    Xppb = 0.5
    Xppd = 0.5
    Xppc = 1#
    XppQ = (Xppb ^ 2 + Xppd ^ 2 + Xppc ^ 2) ^ 0.5
    XQ = (XpQ ^ 2 + XppQ ^ 2) ^ 0.5
    
    scmpXm = rXm
    scmpXb = (scXb / sdbv ^ 2) ^ 0.5
    scmpXd = (scXd / sdbv ^ 2) ^ 0.5
    scmpXe = (scXe / sdbv ^ 2) ^ 0.5
    scmpXp = (scXp / sdbv ^ 2) ^ 0.5
    scmpXc = (scXc / sdbv ^ 2) ^ 0.5
    sumCmp = scmpXm + scmpXb + scmpXd + scmpXe + scmpXp + scmpXc

    suniXm = rXm ^ 2 / XpQ ^ 2
    suniXb = scXb / (sdbv ^ 2 * XpQ ^ 2)
    suniXd = scXd / (sdbv ^ 2 * XpQ ^ 2)
    suniXe = scXe / (sdbv ^ 2 * XpQ ^ 2)
    suniXp = scXp / (sdbv ^ 2 * XpQ ^ 2)
    suniXc = scXc / (sdbv ^ 2 * XpQ ^ 2)
    sumUni = suniXm + suniXb + suniXd + suniXe + suniXp + suniXc
    
   '*****************************************
   '    평균수위 계산
   '*****************************************
    rLave = rLsum / rLnum   '산술평균
   '----------------------------------------------------------------------------------------------
   '저수심일때와 고수심일때로 나누어(기준: 평균수심의 5%=0.05m)
   '수위변화폭에 따른 수위급변의 판단기준을 달리함
   '왜냐하면 저수심일때의 5cm의 수위변화는 수위급변으로 볼수 있지만
   '고수심의 경우는 5cm 수위변화는 수위급변시로 보기 어렵고 평균수심의 5%를 판단기준으로 보아야 함
   '----------------------------------------------------------------------------------------------
    If rPowBlank = 1 Then   '각 측선에서의 수위가 빠지지 않고 기록된 경우
        If rLave < 1# Then  '저수심(평균수심의 5% < 0.05m)
            If (rLmax - rLmin) < 0.05 Then  '수위변화가 0.05m 보다 작으면
                rLave = rLave               '산술평균
            Else                            '수위변화가 0.05m 보다 크면
                rLave = rLPsum / rLDsum     '수위급변시
            End If
        Else                '고수심(평균수심의 5% >= 0.05m)
            If (rLmax - rLmin) < rLave * 0.05 Then  '수위변화가 평균수심의 5% 보다 작으면
                rLave = rLave                       '산술평균
            Else                                    '수위변화가 평균수심의 5% 보다 크면
                rLave = rLPsum / rLDsum             '수위급변시
            End If
        End If
    End If
   
   '*****************************************
    uncCell.Offset(106, 12) = rXm
    uncCell.Offset(106, 4) = sdbv
    uncCell.Offset(106, 11) = sSigma
    uncCell.Offset(106, 13) = XpQ
     
    uncCell.Offset(106, 14) = Xppb
    uncCell.Offset(106, 15) = Xppd
    uncCell.Offset(106, 16) = Xppc
       
    uncCell.Offset(106, 17) = XppQ
        
    uncCell.Offset(106, 18) = XQ
    
    uncCell.Offset(105, 19) = scmpXm
    uncCell.Offset(105, 20) = scmpXb
    uncCell.Offset(105, 21) = scmpXd
    uncCell.Offset(105, 22) = scmpXe
    uncCell.Offset(105, 23) = scmpXp
    uncCell.Offset(105, 24) = scmpXc
    uncCell.Offset(105, 25) = sumCmp
            
    uncCell.Offset(106, 19) = suniXm
    uncCell.Offset(106, 20) = suniXb
    uncCell.Offset(106, 21) = suniXd
    uncCell.Offset(106, 22) = suniXe
    uncCell.Offset(106, 23) = suniXp
    uncCell.Offset(106, 24) = suniXc
    uncCell.Offset(106, 25) = sumUni
      
    outCell.Offset(106, 28) = rLave
'******************************************
'평균수위 계산용(각 측선별 시각과 수위)
'******************************************
    If Sheets("입력시트").CB_dir_start.Text = "LEW" Then
    
        allstCell.Offset(0, 0) = rLtime(1, rTimes)
        allstCell.Offset(0, 1) = rLdepth(1, rTimes)
        alledCell.Offset(0, 0) = rLtime(maxNo, rTimes)
        alledCell.Offset(0, 1) = rLdepth(maxNo, rTimes)
            
    Else
            
        allstCell.Offset(0, 0) = rLtime(maxNo, rTimes)
        allstCell.Offset(0, 1) = rLdepth(maxNo, rTimes)
        alledCell.Offset(0, 0) = rLtime(1, rTimes)
        alledCell.Offset(0, 1) = rLdepth(1, rTimes)
            
    End If
    

    
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
Function Sigma_Error(fdbv2 As Double, fXb As Double, fXd As Double, fXe As Double, fXp As Double, fXc As Double) As Variant
'****************************************************************
' ∑{(b*d*v)^2(Xb^2+Xd^2+Xe^2+Xp^2+Xc^2)}
'
' 2003. 1.
' 황석환
'****************************************************************
Dim rdbv2 As Double
Dim rXb As Double
Dim rXd As Double
Dim rXe As Double
Dim rXp As Double
Dim rXc As Double
'****************************************************************
     rdbv2 = fdbv2
     rXb = frXb
     rXd = fXd
     rXe = fXe
     rXp = fXp
     rXc = fXc
     
     Sigma_Error = rdbv2 * (rXb ^ 2 + rXd ^ 2 + rXe ^ 2 + rXp ^ 2 + rXc ^ 2)
End Function
Sub basicInput()
'****************************************************************
' 기본입력창 띄우기
'****************************************************************
    
'****************************************************************
' 기본정보 클릭시 해당항모에 자료 있을경우 텍스트박스에 값 입력, 기본입력 누를때 자료 삭제 방지
'****************************************************************

With Sheets("종합")



If Len(.Cells(3, 14)) <> 0 Then
    기본입력.T지점명.Text = .Cells(3, 14)
End If

If Len(.Cells(2, 14)) <> 0 Then
    기본입력.T하천명.Text = .Cells(2, 14)
End If

If Len(.Cells(1, 14)) <> 0 Then
    기본입력.TDM.Text = .Cells(1, 14)
End If

If Len(.Cells(4, 14)) <> 0 Then
    기본입력.T위치.Text = .Cells(4, 14)
End If

If Len(.Cells(4, 2)) <> 0 Then
    기본입력.T날짜.Text = .Cells(4, 2)
End If

If Len(.Cells(4, 6)) <> 0 Then
    기본입력.T날씨.Text = .Cells(4, 6)
End If

If Len(.Cells(4, 7)) <> 0 Then
    기본입력.T바람.Text = .Cells(4, 9)
End If

If Len(.Cells(26, 3)) <> 0 Then
    기본입력.T측정자.Text = .Cells(26, 3)
End If

If Len(.Cells(27, 3)) <> 0 Then
    기본입력.T비고.Text = .Cells(27, 3)
End If

End With

If InStr(Sheets("종합").Range("K22"), Chr(10)) Then
                
    With Sheets("입력시트")
                
        If Len(.Cells(1, 246)) <> 0 Then
    
            기본입력.C종류.Text = .Cells(1, 246)
            기본입력.C번호.Text = .Cells(1, 247)
            기본입력.C방식.Text = .Cells(1, 248)
            기본입력.C방법.Text = .Cells(1, 249)
    
        End If
                
        n = 0
                
        Do
         
            n = n + 1
            
            If Len(.Cells(n + 1, 246)) <> 0 Then
            
                기본입력.Controls("Checkbox" & n).Value = True
            
                For i = 1 To 4
                
                    기본입력.Controls("Combobox" & 4 * (n - 1) + i) = .Cells(n + 1, 245 + i)
            
                Next i
            
                기본입력.Controls("Textbox" & n) = .Cells(n + 1, 245 + i)
                
            End If
            
        Loop Until n = 4
    
    End With
    
Else

    With Sheets("종합")
    
        If Len(.Range("K21")) <> 0 Then
        
            기본입력.C종류.Text = .Range("K21")
        
        End If
        
        If Len(.Range("K22")) <> 0 Then
        
            기본입력.C번호.Text = .Range("K22")
        
        End If
                
        If Len(.Range("K27")) <> 0 Then
        
            기본입력.C방법.Text = .Range("K27")
        
        End If
                        
        If Len(Worksheets("이름정의").Range("G11")) <> 0 Then
        
            기본입력.C방식.Text = Worksheets("이름정의").Range("G11")
        
        End If
                
        
    
    End With
    
End If



'****************************************************************
    
    기본입력.Left = 100 '2013.12.05 이기성 수정
    기본입력.T지점명.SetFocus
    기본입력.Show
    
End Sub
Sub bUnCert()
'****************************************************************
' 사전불확실도창 띄우기
'****************************************************************
    사전불확실도.Left = 100
    사전불확실도.Show
End Sub
Function selMeasure() As Integer
'****************************************************************
' 측정회차 결정(현재 활성시트가 1회차 또는 2회차 측정 인지)
' 처음에는 측정시트별로 따로 저장하여 계산하였기 때문에
' 필요했으나 현재는 일괄입력후 일괄계산되기 때문에 사용안함
'****************************************************************
    Select Case Worksheets("이름정의").Range("D11")
        Case "M1"
            selMeasure = 1
           '***지우기
            Worksheets("계산1").Range("B9:AA108").ClearContents
            Worksheets("불확실도1").Range("B9:AA108").ClearContents
        Case "M2"
            selMeasure = 2
           '***지우기
            Worksheets("계산2").Range("B9:AA108").ClearContents
            Worksheets("불확실도2").Range("B9:AA108").ClearContents
    End Select
End Function
'Function calDir() As Integer
'****************************************************************
' 측정방향 설정
'****************************************************************
'    Select Case Worksheets("이름정의").Range("B11")
'        Case "LEW"
'            calDir = 1
'        Case "REW"
'            calDir = 2
'    End Select
'End Function
Function calDir(rTimes As Integer) As Integer
'****************************************************************
' 측정방향 설정
' 측정방향 인식(2004/07/12 수정)
' 각 회차별로 달리 인식가능
'****************************************************************
    Select Case rTimes
        Case 1
            Select Case Worksheets("입력저장1").Range("C8")
                Case "LEW"
                    calDir = 1
                Case "REW"
                    calDir = 2
            End Select
        Case 2
            Select Case Worksheets("입력저장2").Range("C8")
                Case "LEW"
                    calDir = 1
                Case "REW"
                    calDir = 2
            End Select
    End Select
End Function

Function calmaxNo(frngCell As Range) As Integer
'****************************************************************
' 입력 최대측선수 결정
'****************************************************************
    intNo = 0
    Do While frngCell.Offset(intNo + 1, 0) <> ""
        intNo = intNo + 1
    Loop
    calmaxNo = intNo
End Function
Function caldirNo(cdr As Integer, cmaxNo As Integer, cin As Integer) As Integer
'****************************************************************
' 측정방향 측선번호 결정
'****************************************************************
    If cdr = 1 Then
        caldirNo = cin
    ElseIf cdr = 2 Then
        caldirNo = cmaxNo - cin + 1
    Else
        MsgBox "측정방향 설정 오류"
    End If
End Function
Function fNpoint(fnCell1 As Range, fnCell2 As Range, fnCell3 As Range) As Integer
'****************************************************************
' 측점수 결정
'****************************************************************
    Dim rP1 As Integer
    Dim rP2 As Integer
    Dim rP3 As Integer
        If (fnCell1 <> "") Then
            rP1 = 1
        Else
            rP1 = 0
        End If
            
        If (fnCell2 <> "") Then
            rP2 = 1
        Else
            rP2 = 0
        End If
            
        If (fnCell3 <> "") Then
            rP3 = 1
        Else
            rP3 = 0
        End If
            
        fNpoint = rP1 + rP2 + rP3
End Function
Function fnWidth(fw1 As Double, fw2 As Double) As Double
'****************************************************************
' 측선폭 계산
'****************************************************************
    If fw2 >= fw1 Then
        fnWidth = (fw2 - fw1) / 2
    Else
        fnWidth = (fw1 - fw2) / 2
    End If
End Function
Function fnRev(fr1 As Double, ft1 As Double) As Double
'****************************************************************
' 초당회전수 계산
'****************************************************************
    If ft1 = 0 Then
        fnRev = 0
    Else
        fnRev = fr1 / ft1
    End If
End Function
Function fnaveVel(fNoselMeter As Integer, fselMeter As Range, fselMeterNo As Range, frv As Double, frpt As Double) As Double
'****************************************************************
' 측점별 유속계산
'****************************************************************
    Dim meterPara As Range
    Dim paraCri As Double
   '****************************************************
    Dim frvORfrpt As Double '측정범위구분이 회전수인지 아님 초당회전수인지
   '****************************************************
    Dim paraUnit As Double
    Dim paraA1 As Double
    Dim paraB1 As Double
    Dim paraA2 As Double
    Dim paraB2 As Double
    
'    Set meterPara = Worksheets("이름정의").Range("D16")
'
'    paraCri = meterPara.Offset(fNoselMeter, 5)
'    paraUnit = fparaUnit(meterPara.Offset(fNoselMeter, 6)) 'Feet or Meter
'    frvORfrpt = fNorR(meterPara.Offset(fNoselMeter, 6), frv, frpt) 'N(회전수) or R=N/T(초당회전수)
'
'    paraA1 = meterPara.Offset(fNoselMeter, 1)
'    paraB1 = meterPara.Offset(fNoselMeter, 2)
'
'    If meterPara.Offset(fNoselMeter, 3) <> "" Then
'        paraA2 = meterPara.Offset(fNoselMeter, 3)
'        paraB2 = meterPara.Offset(fNoselMeter, 4)
'
    Set meterPara = Worksheets("이름정의").Range("C16")
    
    paraCri = meterPara.Offset(fNoselMeter, 6)
    paraUnit = fparaUnit(meterPara.Offset(fNoselMeter, 7)) 'Feet or Meter
    frvORfrpt = fNorR(meterPara.Offset(fNoselMeter, 7), frv, frpt) 'N(회전수) or R=N/T(초당회전수)
    
    paraA1 = meterPara.Offset(fNoselMeter, 2)
    paraB1 = meterPara.Offset(fNoselMeter, 3)
    
    If meterPara.Offset(fNoselMeter, 4) <> "" Then
        paraA2 = meterPara.Offset(fNoselMeter, 4)
        paraB2 = meterPara.Offset(fNoselMeter, 5)
            
        If frvORfrpt = 0 Then
            fnaveVel = 0#
        ElseIf frvORfrpt <= paraCri Then
            fnaveVel = (paraA1 * frpt + paraB1) * paraUnit
        Else
            fnaveVel = (paraA2 * frpt + paraB2) * paraUnit
        End If
    Else
        If frvORfrpt = 0 Then
            fnaveVel = 0#
        Else
            fnaveVel = (paraA1 * frpt + paraB1) * paraUnit
        End If
    End If
    '********************************
    ' 평균유속이 음수가 되는것 보정
    If fnaveVel < 0 Then
        fnaveVel = 0
    End If
    '********************************
End Function
Function fmVel(faVel2 As Double, faVel6 As Double, faVel8 As Double, TTimes) As Double
'****************************************************************
' 측선별 평균유속계산
'****************************************************************
    'If (faVel2 <> 0 And faVel6 <> 0 And faVel8 <> 0) Then
        'fmVel = 0.25 * (faVel2 + 2 * faVel6 + faVel8)
    'ElseIf (faVel2 <> 0 And faVel8 <> 0) Then
        'fmVel = 0.5 * (faVel2 + faVel8)
    'Else
        'fmVel = faVel6
    'End If

'****************************************************************
' 유속에 관계없이 계산된 점법으로 평균유속계산 2014-01-06 이기성 수정
'****************************************************************
    If TTimes = 3 Then
        fmVel = 0.25 * (faVel2 + 2 * faVel6 + faVel8)
    ElseIf TTimes = 2 Then
        fmVel = 0.5 * (faVel2 + faVel8)
    Else
        fmVel = faVel6
    End If
    
    
End Function
Sub SaveInp()
    Dim maxNo As Integer
    Dim rngCell As Range
    Set rngCell = Worksheets("입력시트").Range("C8")
    '*****************************************
    '    입력저장
    '*****************************************
    maxNo = calmaxNo(rngCell)
    
    Select Case Worksheets("이름정의").Range("D11")
        Case "M1"
            Range(Worksheets("입력저장1").Cells(9, 3), Worksheets("입력저장1").Cells(108, 20)).ClearContents
            Range(Worksheets("입력저장1").Cells(9, 3), Worksheets("입력저장1").Cells(108, 20)).Interior.ColorIndex = xlNone
            
            Worksheets("입력저장1").Range("C8").Offset(0, 0) = Worksheets("입력시트").CB_dir_start
            Worksheets("입력저장1").Range("C8").Offset(101, 0) = Worksheets("입력시트").CB_dir_end
            For i = 1 To maxNo
                Worksheets("입력저장1").Range("C8:s8").Offset(i, 0) = Worksheets("입력시트").Range("C8:s8").Offset(i, 0).Value
            Next i
            
            sh = Sheets("입력저장1").Name
            
            거리계산
            
        Case "M2"
            Range(Worksheets("입력저장2").Cells(9, 3), Worksheets("입력저장2").Cells(108, 20)).ClearContents
            Range(Worksheets("입력저장2").Cells(9, 3), Worksheets("입력저장2").Cells(108, 20)).Interior.ColorIndex = xlNone
            
            Worksheets("입력저장2").Range("C8").Offset(0, 0) = Worksheets("입력시트").CB_dir_start
            Worksheets("입력저장2").Range("C8").Offset(101, 0) = Worksheets("입력시트").CB_dir_end
            For i = 1 To maxNo
                Worksheets("입력저장2").Range("C8:s8").Offset(i, 0) = Worksheets("입력시트").Range("C8:s8").Offset(i, 0).Value
            Next i
            
            sh = Sheets("입력저장2").Name
            
            거리계산
            
    End Select
'    ActiveWorkbook.Save
End Sub
Function fnDisOrder() As Integer
    Dim rngIndex1, rngIndex2, rngIndex3 As Range
    Dim rmb1, rmb2 As Variant
    
    Set rngIndex1 = Worksheets("종합").Range("C34")
    Set rngIndex2 = Worksheets("종합").Range("C35")
    Set rngIndex3 = Worksheets("종합").Range("C36")

    rmb1 = rngIndex2.Offset(0, 0) - rngIndex1.Offset(0, 0)
    rmb2 = rngIndex3.Offset(0, 0) - rngIndex2.Offset(0, 0)
    
    If rmb1 < 0 And rmb2 < 0 Then
        fnDisOrder = -1
    ElseIf rmb1 > 0 And rmb2 > 0 Then
        fnDisOrder = 1
    Else
        fnDisOrder = 0
    End If
End Function
Sub chartM()
    Dim Chartobj As ChartObject
    Dim maxS As Double
    Dim minS As Double
    Dim disOrder As Integer
    
    Dim MySeries As Series
    Dim rngXmaxScale As Range
    Dim rngXminScale As Range
    
    Dim rngXval As Worksheet
    Dim rngYmaxScale As Range
    Dim rngYminScale As Range
  
    Set rngXmaxScale = Worksheets("종합").Range("C135")
    Set rngXminScale = Worksheets("종합").Range("C136")
    
   '****************************************************************
   ' 그래프 출력
   '****************************************************************
'    Set rngXval = Worksheets("계산1")
    Set rngYmaxScale = Worksheets("종합").Range("Z135")
    Set rngYminScale = Worksheets("종합").Range("E135")
    
    Const mUnit = 0.2
    Const mIter = 100   '이경우 유속최대는 0.2 X 100=50 m/s
'****************************************************************
' X값이 "참조"가 되지 않도록 실제 값을 대입
'****************************************************************
    For i = 1 To 5
        Set MySeries = Worksheets("종합").ChartObjects(1).Chart.SeriesCollection(i)
            
            With MySeries
'                .XValues = rngXval.Range("C9:C58") '.Value 안되는 이유는?
                    .XValues = Worksheets("계산1").Range("C9:C108")
            End With
    Next i
    
    Set Chartobj = Worksheets("종합").ChartObjects(1)
'****************************************************************
' X축
'****************************************************************
    With Chartobj.Chart.Axes(xlCategory, xlPrimary)
        .MaximumScale = rngXmaxScale.Value
        .MinimumScale = rngXminScale.Value
        .MajorUnit = Int(.MaximumScale - .MinimumScale) / 20
       '****************************************************************
       ' 측선거리입력에 따른 그래프 X축(측선거리) 정렬순서
       '****************************************************************
        disOrder = fnDisOrder()
        .ReversePlotOrder = False   '순서 초기화
        If disOrder = -1 Then
            .ReversePlotOrder = True
        ElseIf disOrder = 1 Then
            .ReversePlotOrder = False
        ElseIf disOrder = 0 Then
            Call msgBoxDisOrderError
        End If
    End With

'****************************************************************
' Y축(주)
'****************************************************************
    With Chartobj.Chart.Axes(xlValue, xlPrimary)
        maxS = rngYmaxScale.Value
        minS = -1 * (rngYminScale.Value)
        
        For i = 0 To mIter
            If maxS > i * mUnit And maxS < (i + 1) * mUnit Then
               maxS = (i + 1) * mUnit
               Exit For
            End If
        Next i
        
        For j = 0 To mIter
            If minS < -j * mUnit And minS > -(j + 1) * mUnit Then
               minS = -(j + 1) * mUnit
               Exit For
            End If
        Next j
        .MaximumScale = maxS
        .MinimumScale = minS
        
        .MajorUnit = mUnit
    End With
'****************************************************************
' Y축(보조)
'****************************************************************
    With Chartobj.Chart.Axes(xlValue, xlSecondary)
        maxS = rngYminScale.Value
        minS = -1 * (rngYmaxScale)
        
        For i = 0 To mIter
            If maxS > i * mUnit And maxS < (i + 1) * mUnit Then
               maxS = (i + 1) * mUnit
               Exit For
            End If
        Next i
        
        For j = 0 To mIter
            If minS < -j * mUnit And minS > -(j + 1) * mUnit Then
               minS = -(j + 1) * mUnit
               Exit For
            End If
        Next j
        
        .MaximumScale = maxS
        .MinimumScale = minS
        
        .MajorUnit = mUnit
            
    End With
'****************************************************************
End Sub
Sub ChartOnUserform()
   
   Call chartM
      
'   Worksheets("종합").ChartObjects(1).Chart.Export Filename:="Temp.gif", FilterName:="gif"
'   With ufChart.avImage
'      .Picture = LoadPicture("Temp.gif")
'   End With
'   ufChart.avImage.PictureSizeMode = fmPictureSizeModeStretch
  
  '****************************************************************
  ' 최종 계산결과값 도시
  '****************************************************************
   With ufChart
     .tbWidth.Text = Format(Worksheets("종합").Range("BH3").Offset(0, 0), "###0.000")
     .tbLine.Text = Format(Worksheets("종합").Range("BH10").Offset(0, 0), "###0")
     .tbDepth.Text = Format(Worksheets("평균").Range("N11").Offset(0, 0), "###0.000")
     .tbVel.Text = Format(Worksheets("종합").Range("BH8").Offset(0, 0), "###0.000")
     .tbHeight.Text = Format(Worksheets("종합").Range("BH7").Offset(0, 0), "###0.000")
     .tbDis.Text = Format(Worksheets("종합").Range("BH9").Offset(0, 0), "###0.0000")
     .tbUnc.Text = Format(Worksheets("종합").Range("BH13").Offset(0, 0), "###0.00")
   End With
  '****************************************************************
   ufChart.Left = 100 '2013.12.05 이기성 수정
   ufChart.Show
'   Kill "Temp.gif"
      
End Sub
Sub addDBmain()
    Dim rngDBName As Range
    Set rngDBName = Workbooks("DBFPAD.XLS").Worksheets("DB").Range("B5").End(xlDown).Offset(1, 0)
'    Set rngDBName = Workbooks("DBFPAD").Worksheets("DB").Range("B5").End(xlDown).Offset(1, 0)
    
    Call addDB(rngDBName)

End Sub
Sub addDB(frngCell As Range)
    Dim rngCell As Range
    Set rngCell = frngCell.Offset(0, 0)
    With rngCell
        .Offset(0, 0) = Worksheets("평균").Range("D5")
        For i = 0 To 6
            .Offset(0, i + 1) = Worksheets("평균").Range("D11").Offset(0, i)
        Next i
        For j = 0 To 2
            .Offset(0, j + 12) = Worksheets("평균").Range("D11").Offset(0, j + 7)
        Next j
        For k = 0 To 6
            .Offset(0, k + 15) = Worksheets("평균").Range("D17").Offset(0, k)
        Next k
        For l = 0 To 5
            .Offset(0, l + 22) = Worksheets("평균").Range("D23").Offset(0, l)
        Next l
        For M = 0 To 6
            .Offset(0, M + 28) = Worksheets("평균").Range("D29").Offset(0, M)
        Next M
            .Offset(0, 35) = Worksheets("평균").Range("D11").Offset(0, 10) '평균수심
            .Offset(0, 36) = Worksheets("평균").Range("M5") '시작-종료 시간
    End With
End Sub
Sub helpMsg()
    Worksheets("도움말").Activate
End Sub
Function fIndxBlank(fLdepth As Variant) As Double
    If fLdepth = "" Then
        fIndxBlank = 0
    Else
        fIndxBlank = 1
    End If
End Function
Function frRev(fselMeter As Range, fmrRev As Double) As Variant
'    If fselMeter = "유속입력" Then
    If fselMeter = "유속" Then
        frRev = ""
    Else
        frRev = fmrRev
    End If
End Function
Function fNorR(fparaIndex As Range, frev As Double, frevT As Double) As Double
    Select Case fparaIndex
        Case "F[N]", "M[N]"
            fNorR = frev
        Case "F[R]", "M[R]"
            fNorR = frevT
        Case Default
            MsgBox "검정식구분인자오류(회전수 or 초당회전수?)"
    End Select
End Function
Function fparaUnit(fmeterPara As Range) As Double
    Select Case fmeterPara
        Case "M[N]", "M[R]"
            fparaUnit = 1#
        Case "F[N]", "F[R]"
            fparaUnit = 0.3048
        Case Else
            MsgBox "단위설정오류"
        End
    End Select
End Function
Function fNoselMeter() As Integer
    'Dim meterPara As Range
    'Dim selMeterPara As Range
    'Dim intNo As Integer
    'Set selMeterPara = Worksheets("종합").Range("K22")
    'Set meterPara = Worksheets("이름정의").Range("C16")

    'intNo = 1
    'Do While meterPara.Offset(intNo, 0) <> ""
        'If meterPara.Offset(intNo, 0) = selMeterPara Then
            'fNoselMeter = intNo
        'End If
        'intNo = intNo + 1
    'Loop

    Dim meterPara As Range
    'Dim selMeterPara As Range'유속계 2개 이상 사용을 위해 public으로 변수선언 이기성 수정
    Dim intNo As Integer
    'Set selMeterPara = Worksheets("종합").Range("K22")
    Set meterPara = Worksheets("이름정의").Range("C16")

    intNo = 1
    Do While meterPara.Offset(intNo, 0) <> ""
        If meterPara.Offset(intNo, 0) = selMeterPara Then
            fNoselMeter = intNo
        End If
        intNo = intNo + 1
    Loop

    loc = fNoselMeter







End Function
'Function fNoselMeter() As Integer
'    Dim meterPara As Range
'    Dim selMeterPara As Range
'    Dim intNo As Integer
'    Set selMeterPara = Worksheets("종합").Range("K23")
'    Set meterPara = Worksheets("이름정의").Range("D16")'
'
'    intNo = 1
'    Do While meterPara.Offset(intNo, 0) <> ""
'        If meterPara.Offset(intNo, 0) = selMeterPara Then
'            fNoselMeter = intNo
'        End If
'        intNo = intNo + 1
'    Loop
'End Function


