/* global  plotFunctionanalysis1,crossFilterDict */

function masterUserConfigPlot (chartConfigDict) { // eslint-disable-line no-unused-vars
  for (const i in chartConfigDict) {
    const elementTabID = i
    crossFilterDict[i] = []
    const userPlotDataFinal = Array.from(chartConfigDict[i])
    for (let j = 0; j < userPlotDataFinal.length; j++) {
      const plotType = userPlotDataFinal[j].chartType
      const x = userPlotDataFinal[j].xAxis
      const y = userPlotDataFinal[j].yAxis
      const xE = userPlotDataFinal[j].xEAxis
      const yE = userPlotDataFinal[j].yEAxis
      const color = userPlotDataFinal[j].color
      const xLabel = userPlotDataFinal[j].xLabel
      const yLabel = userPlotDataFinal[j].yLabel
      const tableName = userPlotDataFinal[j].tableName
      const gridlines = userPlotDataFinal[j].gridlines
      const xRangeStart = userPlotDataFinal[j].xRangeStart
      const xRangeEnd = userPlotDataFinal[j].xRangeEnd
      const yRangeStart = userPlotDataFinal[j].yRangeStart
      const yRangeEnd = userPlotDataFinal[j].yRangeEnd
      const plotDict = { plotType: plotType, x: x, y: y, xE: xE, yE: yE, color: color, chartHeader: userPlotDataFinal[i].chartHeader, tableName: tableName, xLabel: xLabel, yLabel: yLabel, gridlines: gridlines, xRangeStart: xRangeStart, xRangeEnd: xRangeEnd, yRangeStart: yRangeStart, yRangeEnd: yRangeEnd }
      plotFunctionanalysis1(plotDict, elementTabID)
    }
  }
}
