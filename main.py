import yaml
import schedule
import requests
import time
import logging

logging.basicConfig(handlers=[
    logging.FileHandler("log/data.log"),
    logging.StreamHandler()],
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger("grafana_silence")


def do_silence(alert_id, target):
    logger.info(f"Running silence for {alert_id}")
    response = requests.post(f"{target['url']}/api/alerts/{alert_id}/pause", headers={
                             'Authorization': f"Bearer {target['token']}"}, data={'paused': True})
    logger.debug("Status code:", response.status_code)
    logger.debug("Response:", response.text)


def do_unsilence(alert_id, target):
    logger.info(f"Running unsilence for {alert_id}")
    response = requests.post(f"{target['url']}/api/alerts/{alert_id}/pause", headers={
                             'Authorization': f"Bearer {target['token']}"}, data={'paused': False})
    logger.debug("Status code:", response.status_code)
    logger.debug("Response:", response.text)


def timestring_to_minutes(timestamp):
    return int(timestamp.split(':')[0]) * 60 + int(timestamp.split(':')[1])


def minutes_to_timestring(minutes):
    return f"{str((minutes // 60) % 24).rjust(2, '0')}:{str(minutes % 60).rjust(2, '0')}"


def get_silence_time(start_time, end_time):
    start_minutes = timestring_to_minutes(start_time)
    end_minutes = timestring_to_minutes(end_time)
    if end_minutes < start_minutes:
        end_minutes += 24 * 60
    silence_times = []
    while start_minutes < end_minutes:
        silence_times.append(minutes_to_timestring(start_minutes))
        start_minutes += 8 * 60
    return silence_times


def init(alert_id, start_time, end_time, target):
    logger.info(
        f"Registering alert silence for {alert_id} start at {start_time} end at {end_time}")
    silence_times = get_silence_time(start_time, end_time)
    for silence_time in silence_times:
        schedule.every().day.at(silence_time).do(lambda: do_silence(alert_id, target))
    schedule.every().day.at(end_time).do(lambda: do_unsilence(alert_id, target))


if __name__ == "__main__":
    with open('config.yaml', 'r') as file:
        data = yaml.safe_load(file)
        for silence in data['silences']:
            try:
                target = [target for target in data['targets']
                          if target['name'] == silence['target']][0]
                init(silence['alert_id'], silence['start_time'],
                     silence['end_time'], target)
            except Exception as e:
                logger.error(e)

    while True:
        schedule.run_pending()
        time.sleep(1)
