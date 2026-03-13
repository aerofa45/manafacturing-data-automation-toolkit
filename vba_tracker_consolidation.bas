Attribute VB_Name = "Module1"
Option Explicit

' Manufacturing Operations Toolkit
' Consolidates production data from all worksheets with names containing "Shift"
' into a single Weekly_Summary sheet and applies KPI formulas.

Sub FinalizeWeeklyReport()
    Dim ws As Worksheet
    Dim destWs As Worksheet
    Dim lastRow As Long
    Dim nextRow As Long
    Dim headersWritten As Boolean

    Set destWs = ThisWorkbook.Worksheets("Weekly_Summary")

    destWs.Cells.ClearContents
    headersWritten = False
    nextRow = 1

    For Each ws In ThisWorkbook.Worksheets
        If InStr(1, ws.Name, "Shift", vbTextCompare) > 0 Then
            lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row

            If lastRow >= 2 Then
                If Not headersWritten Then
                    ws.Range("A1:F1").Copy Destination:=destWs.Range("A1")
                    destWs.Range("G1").Value = "Quality_Yield"
                    destWs.Range("H1").Value = "Scrap_Rate"
                    headersWritten = True
                    nextRow = 2
                End If

                ws.Range("A2:F" & lastRow).Copy Destination:=destWs.Range("A" & nextRow)
                nextRow = destWs.Cells(destWs.Rows.Count, "A").End(xlUp).Row + 1
            End If
        End If
    Next ws

    lastRow = destWs.Cells(destWs.Rows.Count, "A").End(xlUp).Row

    If lastRow >= 2 Then
        destWs.Range("G2:G" & lastRow).Formula = "=IF(C2=0,0,E2/C2)"
        destWs.Range("H2:H" & lastRow).Formula = "=IF(C2=0,0,F2/C2)"

        destWs.Range("G2:H" & lastRow).NumberFormat = "0.00%"
        destWs.Columns("A:H").AutoFit

        MsgBox "Weekly production report consolidated successfully.", vbInformation
    Else
        MsgBox "No shift data found to consolidate.", vbExclamation
    End If
End Sub
