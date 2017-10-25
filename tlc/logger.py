from datetime import datetime,timedelta,tzinfo

def logger(message_type, args, conf_file, local_codes, output_file):
    message = ''
    if(message_type == 'start'):
        with open(output_file, "a") as text_file:
            message += 'STARTING LOADING PROCESS \n'
            message += 'Page name: ' + conf_file["webpage"]["name"] + '\n'
            message += 'Main URL: ' + conf_file["webpage"]["uri_start"] + '\n'
            message += 'Page Type: ' + str(conf_file["webpage"]["page_type"]) + '\n'
            message += 'Number of cities to load: ' + str(len(local_codes["codes"])) + '\n'
            message += 'Number of days to load: ' + str(conf_file["webpage"]["date_span_finish"] - conf_file["webpage"]["date_span_start"]) + '\n'
            message += 'Started at: ' + datetime.now().strftime('%d-%m-%Y %H:%M:%S') + '\n'
            print message
            text_file.write(message)
    elif(message_type == 'end'):
        end_time = datetime.now()
        duration = end_time - args[1]
        with open(output_file, "a") as text_file:
            message += 'ENDING LOADING PROCESS \n'
            message += 'Number of loaded travels: ' + str(args[0]) + '\n'
            message += 'Ended at: ' + datetime.now().strftime('%d-%m-%Y %H:%M:%S') + '\n'
            message += 'Total duration: ' + duration.strftime('%d-%m-%Y %H:%M:%S') + '\n'
            message += '----------------------------------------------------' + '\n'
            print message
            text_file.write(message)
