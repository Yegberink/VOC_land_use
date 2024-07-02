library(tidyverse)

# Function to process each file
process_file <- function(file_path) {
  lines <- readLines(file_path)
  text <- paste(lines, collapse = "")
  text <- str_remove_all(text, disclaimer_pattern)
  matches <- str_locate_all(text, split_pattern)[[1]]
  document_count <- nrow(matches)
  
  if (document_count == 0) {
    cat("No documents found in file:", file_path, "\n")
    return(NULL)
  }
  
  label_identifiers <- character(document_count) 
  document_content <- character(document_count)
  
  for (j in 1:document_count) {
    start_pos <- matches[j, "end"] + 1
    end_pos <- ifelse(j < document_count, matches[j + 1, "start"] - 1, nchar(text))
    label_identifiers[j] <- substr(text, matches[j, "start"] + 3, matches[j, "start"] + 28)
    document_content[j] <- substr(text, start_pos, end_pos)
  }
  
  df <- tibble(
    LabelIdentifier = label_identifiers,
    DocumentContent = document_content
  )
  
  return(df)
}

disclaimer_pattern <- "\\*{10,}.*?\\*{10,}.*?(?=-{3,})"
split_pattern <- "---(NL-HaNA_1\\.04\\.02_\\d+_\\d+\\.xml)---"

# Load data
file_paths <- list.files("Data/VOC_data", full.names = TRUE, recursive = FALSE)

# Process files in parallel
files <- lapply(file_paths, process_file)

# Remove NULL elements
files <- files[!sapply(files, is.null)]

# Combine into a single dataframe
files_df <- bind_rows(files)

# Save the dataframe to RData file
save(files, file = "/Users/Yannick/Documents/Thesis 2024/VOC_data.rdata")

# Save the dataframe to a CSV file
write_csv(files_df, file = "/Users/Yannick/Documents/Thesis 2024/files.csv")
