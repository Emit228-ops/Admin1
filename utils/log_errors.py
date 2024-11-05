def log_error(message):
  with open("error_log.txt", "a") as file:
      file.write(f"{message}\n")
