from datetime import datetime,timedelta,tzinfo
import unicodedata

def logger(message_type, args, conf_file, local_codes, output_file, my_lock):
    message = ''
    my_lock.acquire()
    text_file = open(output_file, "a")
    if(message_type == 'start'):
        message += '\nLOADING PROCESS STARTED\n'
        message += 'Page name: ' + conf_file["webpage"]["name"] + '\n'
        message += 'Main URL: ' + conf_file["webpage"]["uri_start"] + '\n'
        message += 'Page Type: ' + str(conf_file["webpage"]["page_type"]) + '\n'
        message += 'Number of cities to load: ' + str(len(local_codes["codes"])) + '\n'
        message += 'Number of days to load: ' + str(conf_file["webpage"]["date_span_finish"] - conf_file["webpage"]["date_span_start"]) + '\n'
        message += 'Started at: ' + datetime.now().strftime('%d-%m-%Y %H:%M:%S') + '\n'
    elif(message_type == 'end'):
        end_time = datetime.now()
        duration = end_time - args[2]
        message += 'LOADING PROCESS ENDED\n'
        message += 'Number of travels loaded: ' + str(args[0])
        if(args[0] != args[1]):
            message += '(plus ' + str(args[1] - args[0]) + ' pruned)'
        message += '\n'
        message += 'Ended at: ' + datetime.now().strftime('%d-%m-%Y %H:%M:%S') + '\n'
        message += 'Time spent loading: ' + str(duration) + '\n'
        message += '----------------------------------------------------' + '\n'

    elif(message_type == 'agency'):
        if(args[0] == ''):
            message += 'WARNING: No travel agencies were found for a travel coming from ' + args[1].name + ' to ' + args[2].name + ' the ' + str(args[3]) + '. Using Generic travel agency instead.\n'
        else:
            message += 'WARNING: Unknown travel agency ' + args[0] + ' found, using Generic travel agency instead. If you want ' + args[0] + ' to be shown in the webpage add it to the database first as a new travel agency or as an alias of an exisiting one.\n'
    elif(message_type == 'error'):
        if(args[0] == 0):
            message += 'ERROR: While loading config file. Check the file for errors.\n'
        elif(args[0] == 1):
            message += 'ERROR: No departure tag was found for a travel from ' + args[1].name + ' to ' + args[2].name + ' the ' + str(args[3]) + '. Check the config file for errors or check if the webpage has changed.\n'
        elif(args[0] == 2):
            message += 'ERROR: No duration or arrival tags were found for a travel from ' + args[1].name + ' to ' + args[2].name + ' the ' + str(args[3]) + '. Check the config file for errors or check if the webpage has changed.\n'
        elif(args[0] == 3):
            message += 'ERROR: No price tag was found for a travel from ' + args[1].name + ' to ' + args[2].name + ' the ' + str(args[3]) + '. Check the config file for errors or check if the webpage has changed.\n'
        elif(args[0] == 4):
            message += 'ERROR: No travel agency tag was found for a travel from ' + args[1].name + ' to ' + args[2].name + ' the ' + str(args[3]) + '. Check the config file for errors or check if the webpage has changed.\n'
        elif(args[0] == 5):
            message += 'ERROR: While creating travel instances coming from ' + args[1].name + ' to ' + args[2].name + ' the ' + str(args[3]) + '. Check the config file for errors or check if the webpage has changed.\n'
        elif(args[0] == 6):
            message += 'ERROR: While creating travel blocks from '+ args[1].name + ' to ' + args[2].name + ' the ' + str(args[3]) + '. Check the config file for errors or check if the webpage has changed.\n'
        elif(args[0] == 7):
            message += 'ERROR: While spliting the HTML into travel blocks. Check the config file for errors or check if the webpage has changed.\n'
        elif(args[0] == 8):
            message += 'ERROR: While executing javascript to access travels from ' + args[1].name + ' to ' + args[2].name + ' the ' + str(args[3]) + '. Check the config file for errors or check if the webpage has changed.\n'
        elif(args[0] == 9):
            message += 'ERROR: While creating the URL to access travels from ' + args[1].name + ' to ' + args[2].name + ' the ' + str(args[3]) + '. Check the config file for errors or check if the webpage has changed.\n'
        elif(args[0] == 10):
            message += 'ERROR: While parsing the string ' + args[1]
            if(args[2] != ''):
                message += ' with the regular expression ' + args[2]
            if(args[3] != ''):
                message += ' and with the formula ' + args[3]
            message += '\n'
    elif(message_type == 'warning'):
        if(args[0] == 1):
            message += 'WARNING: No departure tag was found for a travel from ' + args[1].name + ' to ' + args[2].name + ' the ' + str(args[3]) + '. The travel will be skipped.\n'
        elif(args[0] == 2):
            message += 'WARNING: No duration or arrival tags were found for a travel from ' + args[1].name + ' to ' + args[2].name + ' the ' + str(args[3]) + '. The travel will be skipped\n'
        elif(args[0] == 3):
            message += 'WARNING: No price tag was found for a travel from ' + args[1].name + ' to ' + args[2].name + ' the ' + str(args[3]) + '. The travel will be skipped.\n'
        elif(args[0] == 4):
            message += 'WARNING: No travel agency tag was found for a travel from ' + args[1].name + ' to ' + args[2].name + ' the ' + str(args[3]) + '. The travel will be skipped.\n'
        elif(args[0] == 5):
            message += 'WARNING: While creating a travel instance coming from ' + args[1].name + ' to ' + args[2].name + ' the ' + str(args[3]) + '. The travel will be skipped.\n'
        elif(args[0] == 6):
            message += 'WARNING: No travel blocks were created after splitting the HTML. Check the config file for errors or check if the webpage has changed.\n'
    elif(message_type == 'no_travels'):
        message += 'WARNING: No travels where loaded to the database. Previous travels from this webpage will remain in the system but they will be marked as out of date.'
    elif(message_type == 'config_file'):
        message += 'ERROR: While loading config file ' + args[0] + '. Check the file for errors.\n'
    elif(message_type == 'connection'):
        message += 'ERROR: Connection error while loading the webpage for travels from ' + args[0] + ' to ' + args[1] + ' the ' + args[2] + '. Check the file for errors.\n'

    # print message
    if(isinstance(message, unicode)):
        message = unicodedata.normalize('NFKD', message).encode('ascii','ignore')
    text_file.write(message)
    my_lock.release()
