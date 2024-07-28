from datetime import datetime
from datetime import timedelta


"""
Give a source and destination port returns the rates for a particular day"""
def _get_port_rates_for_date(source, destination, single_date, cur):
    cur.execute('''SELECT price FROM prices where orig_code=%s\
                    AND dest_code=%s AND day=%s''', (source, destination, single_date,))
    prices = cur.fetchall()
    if not prices:
        return 0, 0
    total_rates = sum([price[0] for price in prices])
    number_of_rates = len(prices)
    return total_rates, number_of_rates


"""
Given two lists of ports returns total rates and number of dates for each dat in a timerange
"""
def _get_avg_port_rates_by_dates(source_ports: list, destination_ports: list, date_from: datetime, date_to: datetime, cur):
    rates_dict = {}
    days = int((date_to - date_from).days)
    for n in range(days+1):
        rates_dict[str(date_from + timedelta(n))] = {"total_rate": 0, "number_of_rates": 0}
    for s_port in source_ports:
        for d_port in destination_ports:
            single_date = date_from
            while single_date <= date_to:
                sum_rates, number_of_rates = _get_port_rates_for_date(s_port, d_port, single_date, cur)
                if number_of_rates != 0:
                    rates_dict[str(single_date)]["number_of_rates"] += number_of_rates
                    rates_dict[str(single_date)]["total_rate"] += sum_rates
                single_date += timedelta(days=1)
    return rates_dict

"""
Recursively goes through regions to return all child ports
"""
def _get_child_ports(regions: list, child_ports: list, cur):
    # TODO: Set limit on query
    cur.execute(f'''SELECT p.code, r2.slug FROM regions r1 \
                        LEFT JOIN ports p ON r1.slug = p.parent_slug\
                        LEFT JOIN regions r2 ON r1.slug = r2.parent_slug \
                        WHERE p.parent_slug in (SELECT unnest(%s))
                        OR r2.parent_slug in (SELECT unnest(%s))''', (regions, regions,))

    children = cur.fetchall()
    child_ports.extend([child[0] for child in children if child[0]])
    child_ports = list(set(child_ports))
    regions = [child[1] for child in children if child[1]]
    regions = list(set(regions))
    if not regions:
        return child_ports
    return _get_child_ports(regions, child_ports, cur)


"""
Checks if the given vode belongs to a port
"""
def _is_port(port, cur):
    cur.execute('''SELECT 1 FROM ports where code = %s''', (port,))
    port = cur.fetchone()
    if not port:
        return 0
    return 1


"""
Returns a list of ports given a region
If the input is a port returns the port
"""
def _get_children_ports(source, cur):
    _is_source_port = _is_port(source, cur)
    if _is_source_port:
        return [source]

    if _is_source_port:
        child_source_ports = [source]
    else:
        child_source_ports = _get_child_ports(regions=[source], child_ports=[], cur=cur)

    return child_source_ports


"""
Compute average daily shipping rates given source and destination ports or slugs  and a daterange
"""
def get_rates(source, destination, date_from, date_to, cur):

    child_source_ports = _get_children_ports(source, cur)
    child_dest_ports = _get_children_ports(destination, cur)
    rates = _get_avg_port_rates_by_dates(child_source_ports, child_dest_ports, date_from, date_to, cur)
    cur.close()

    rate_list = []
    for single_date, rate in rates.items():
        if rate["number_of_rates"] == 0:
            avg_price_for_date = None
        else:
            avg_price_for_date = int(round(rate["total_rate"]/rate["number_of_rates"]))
        rate_list.append({"day": single_date, "average_price": avg_price_for_date})

    return rate_list
