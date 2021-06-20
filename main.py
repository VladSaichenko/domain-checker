import csv
import multiprocessing as mp
from os import listdir, remove

from fake_headers import Headers
from requests import Session, exceptions


def divide_list(lst, n):
    amt = len(lst) // n
    for _ in range(n):
        yield lst[:amt]
        lst = lst[amt:]


def get_domain(url) -> str:
    return url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]


def check_domain(domain: str, session: Session) -> dict:
    """ Checks the domain and returns a dict object containing information about it """
    redirect_domains = []

    try:
        response = session.get('https://' + domain)
    except exceptions.SSLError:
        try:
            response = session.get('http://' + domain)
        except exceptions.SSLError:
            return dict(domain=domain, accessible=False, redirect_domains=redirect_domains, status_code=None)
    except exceptions.ConnectionError:
        return dict(domain=domain, accessible=False, redirect_domains=redirect_domains, status_code=None)

    if response.history:
        redirect_domains = list(map(lambda x: get_domain(x.url), response.history))

    return dict(
        domain=domain,
        accessible=(response.status_code == 200),
        redirect_domains=redirect_domains,
        status_code=response.status_code
    )


def parse_and_create_temp_files(domains):
    """
        Temporary files are saved with names in 'temp_file_<ID>.csv' format.
        They will be deleted later automatically.
    """
    header = Headers(os='win', browser='Chrome', headers=True)
    session = Session()

    with open(f'temp_file_{mp.current_process().pid}.csv', 'w') as file:
        writer = csv.writer(file, delimiter=';')

        for domain in domains:
            session.headers.update(header.generate())
            data = check_domain(domain, session)

            writer.writerow([
                data['domain'],
                'yes' if data['accessible'] else 'no',
                ', '.join(data['redirect_domains']) if data['redirect_domains'] else '',
                data['status_code'] if data['status_code'] else ''
            ])


def collect_data():
    """ Combines data from `temp_file_` files to result.csv """
    file_names = list(filter(lambda x: 'temp_file_' in x, listdir()))

    with open('result.csv', 'w') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['domain', 'domain_status', 'redirected_domains', 'status_code'])

        for file_name in file_names:
            with open(file_name, 'r') as temp_file:
                reader = csv.reader(temp_file, delimiter=';')
                for row in reader:
                    writer.writerow(row)
            remove(file_name)  # Removes temp file after appending its data to result.csv


if __name__ == '__main__':
    with open('domains.csv', 'r') as file:
        reader = csv.reader(file, delimiter=',')
        domains = list(map(lambda x: x[0], list(reader)[1:]))

    cpus = mp.cpu_count() * 2 + 1
    with mp.Pool(processes=cpus) as p:
        p.map(parse_and_create_temp_files, list(divide_list(domains, cpus)))

    collect_data()
