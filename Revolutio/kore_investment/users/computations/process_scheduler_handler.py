from datetime import datetime, timedelta

from kore_investment.users import scheduler as schedulerfunc


def schedule_block(request, block_id, block_config, subprocess_code, process_code, b_index=0):
    retries = block_config["noOfRetries"]
    interval_between_retries = block_config["intervalBetweenRetries"]
    block_trigger_onfig = block_config["blockTriggerConfig"]
    start_date = block_trigger_onfig["startDate"]
    end_date = block_trigger_onfig["endDate"]
    duration = block_trigger_onfig["intervalPeriod"]
    time = block_trigger_onfig["intervalTime"]
    if block_trigger_onfig.get("intervalFrequency"):
        frequency = block_trigger_onfig["intervalFrequency"]
    else:
        frequency = "1"

    month, day_of_week, day, hour, minute = cron_time_convertor(
        start_date, duration, time, frequency=frequency
    )
    func = "schedulercheck.execute_block"
    job_id = f"{subprocess_code}_{block_id}_{b_index}"
    schedulerfunc.process_flow_scheduler(
        func,
        job_id,
        request,
        month,
        day_of_week,
        day,
        hour,
        minute,
        retries,
        interval_between_retries,
        start_date,
        end_date,
        block_config=block_config,
    )
    return None


def schedule_flow(request, flow_schedule_config, subprocess_code, process_code):
    retries = flow_schedule_config["noOfRetries"]
    interval_between_retries = flow_schedule_config["intervalBetweenRetries"]
    start_date = flow_schedule_config["startDate"]
    end_date = flow_schedule_config["endDate"]
    duration = flow_schedule_config["intervalPeriod"]
    time = flow_schedule_config["intervalTime"]
    if flow_schedule_config.get("intervalFrequency"):
        frequency = flow_schedule_config["intervalFrequency"]
    else:
        frequency = "1"

    month, day_of_week, day, hour, minute = cron_time_convertor(
        start_date, duration, time, frequency=frequency
    )
    func = "schedulercheck.execute_flow"
    job_id = f"{process_code}_{subprocess_code}"
    schedulerfunc.process_flow_scheduler(
        func,
        job_id,
        request,
        month,
        day_of_week,
        day,
        hour,
        minute,
        retries,
        interval_between_retries,
        start_date,
        end_date,
    )
    return None


def cron_time_convertor(start_date, duration, time, frequency="1"):
    if type(start_date) == str:
        start_date = datetime.strptime(start_date + " " + time + ":00", "%Y-%m-%d %H:%M:%S")
    else:
        pass
    if duration == "Monthly":
        day = start_date.day
        month = "*"
        day_of_week = "*"
    elif duration == "Monthly/5th day":
        day = "5"
        month = "*"
        day_of_week = "*"
    elif duration == "Quarterly":
        day = start_date.day
        month = "1,4,7,10"
        day_of_week = "*"
    elif duration == "Pre-Quarterly":
        day = "24"
        month = "12,3,6,9"
        day_of_week = "*"
    elif duration == "Weekly":
        day_of_week = start_date.weekday()
        month = "*"
        day = "*"
    elif duration == "Daily":
        month = "*"
        day = "*"
        day_of_week = "*"
    elif duration == "Yearly":
        month = start_date.month
        day = start_date.day
        day_of_week = "*"
    elif duration == "Hourly":
        month = "*"
        day = "*"
        day_of_week = "*"
        hour = f"*/{frequency}"
    elif duration == "Every N Minutes":
        month = "*"
        day = "*"
        day_of_week = "*"
        hour = "*"
        minute = f"*/{frequency}"

    utc_offset = datetime.utcnow() - datetime.now() + timedelta(minutes=1)
    utc_datetime = start_date + utc_offset
    utc_datetime = str(utc_datetime).split(" ")
    time_var = utc_datetime[1]
    if duration not in ["Hourly", "Every N Minutes"]:
        if time_var.split(":")[0][0] == "0":
            hour = eval(time_var.split(":")[0][1])
        else:
            hour = eval(time_var.split(":")[0])
    if duration != "Every N Minutes":
        if time_var.split(":")[1][0] == "0":
            minute = eval(time_var.split(":")[1][1])
        else:
            minute = eval(time_var.split(":")[1])
    return month, day_of_week, day, hour, minute
