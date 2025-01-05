# Required libraries
install.packages("log4r")  # Install log4r package if not already installed
library(randomForest)
library(caret)
library(ROCR)
library(log4r)

# Setting up the log file
logger <- create.logger()
logfile(logger) <- "../CodeGenesis-TEAM/reports/logs/model_logs.log"  # Specify a file name for the log file
level(logger) <- "INFO"

# Loading the data
data <- read.csv("../CodeGenesis-TEAM/data/processed/cleaned_us_death_rates.csv")
info(logger, "Data loaded successfully.")

# Transforming and categorizing the target variable
data$Risk_Level <- ifelse(data$Death_rate_weekly_of_unvaccinated_people_United_States_by_age > 10, 1, 0)
data$Risk_Level <- as.factor(data$Risk_Level)
info(logger, "Target variable transformed and categorized.")

# Splitting the data into training and testing sets
set.seed(42)
trainIndex <- createDataPartition(data$Risk_Level, p = 0.8, list = FALSE)
trainData <- data[trainIndex, ]
testData <- data[-trainIndex, ]
info(logger, "Data split into training and testing sets.")

# Random Forest Model (Classification Mode)
rfModel <- randomForest(Risk_Level ~ ., data = trainData, ntree = 100, importance = TRUE)
info(logger, "Random Forest model trained.")
print(rfModel)

# Predictions and Performance Evaluation
pred <- predict(rfModel, testData, type = "response")
confMat <- confusionMatrix(as.factor(pred), as.factor(testData$Risk_Level))
info(logger, "Model predictions made and performance evaluated.")
print(confMat)

# ROC Curve
pred_prob <- predict(rfModel, testData, type = "prob")[, 2]
pred_obj <- prediction(pred_prob, as.numeric(as.character(testData$Risk_Level)))
roc_perf <- performance(pred_obj, "tpr", "fpr")
png(filename = "../CodeGenesis-TEAM/reports/logs/roc_curve.png")
plot(roc_perf, colorize = TRUE, main = "ROC Curve - Random Forest (R)")
dev.off()
info(logger, "ROC curve plotted and saved as 'roc_curve.png'.")

# AUC Score
auc <- performance(pred_obj, measure = "auc")
cat("\nAUC Score:", auc@y.values[[1]], "\n")
info(logger, paste("AUC Score:", auc@y.values[[1]]))

# Important Variables
varImpPlot(rfModel, main = "Variable Importance - Random Forest (R)")
info(logger, "Variable importance plotted.")

# Saving the Model
save(rfModel, file = "../CodeGenesis-TEAM/reports/logs/rfModel.RData")
info(logger, "Model saved as 'rfModel.RData'.")