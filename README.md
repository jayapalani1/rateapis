# Rate APIs

## Setup
### Pre-requisite 1: Python3.10+
### Pre-requisite 2: Make sure the `ratetask` postgres instance is running.

Run the following commands to install the required packages for rateapis

```virtualenv venv```

```source venv/bin/activate```

```pip install -r requirements.txt```

## API endpoints
### /rates
API to get average rates per day between ports or regions
+ origin - port code/region slug from where shipment is to be sent
+ destination - port code/region slug to where shipment is sent
+ date_from - starting of a date range
+ date_end - ending of date range

If origin or destination is a region then the API recursively gets all\
the ports attached with the region and sub-regions




