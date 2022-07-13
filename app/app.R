library(shiny)
library(vroom)

#rikers <- vroom("dat/clean/DIC-06012016-06022022.csv")
start.date <- min(rikers$date)
end.date <- max(rikers$date)

ui <- fluidPage(
  titlePanel("Hello Shiny!"),
  sidebarLayout(
    sidebarPanel(
      actionButton('update', "Update!")
        ),
    mainPanel(
      plotOutput("distPlot"),
      sliderInput('viewDate', "", min = start.date, max = end.date, value = c(start.date, end.date), timeFormat = "%m-%d-%y", width = "100%")
    )
  )
)

server <- function(input, output, session) {
  rikersData <- eventReactive(input$update, {
    filter(rikers, date > input$viewDate[1], date <= input$viewDate[2]) %>%
      count(date)
  }, ignoreInit = T)
  
  output$distPlot <- renderPlot({
    if (nrow(rikersData() == 1)) {
      ggplot(rikersData(), aes(x = date, y=n)) + 
        geom_line() + 
        theme(panel.grid = element_blank())
      } else {
      ggplot(rikersData(), aes(x = date, y=n)) + 
        geom_col() + 
        theme(panel.grid = element_blank())
    }
  }, res = 96)
}

shinyApp(ui, server)