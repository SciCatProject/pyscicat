# Pyscicat

Pyscicat is a python client library for interacting with the [SciCat backend](https://scicatproject.github.io/). It sends messages to the SciCat backend over HTTP. It currently does not contain any command line interface.

Documentation for Pyscicat is [available here](https://scicatproject.github.io/pyscicat/).

### Basic usage example

```python
from datetime import datetime

from pyscicat.client import ScicatClient 
from pyscicat.model import (Ownable, RawDataset, DatasetType, Sample)

# Create a client object. The account used should have the ingestor role in SciCat
client = ScicatClient(base_url="http://localhost/api/v3", username="admin", password="2jf70TPNZsS")

ownable = Ownable(ownerGroup="aGroup", accessGroups=[])

# Create a Dataset object. Notice how we pass the `ownable` instance.
dataset = RawDataset(
    size=42,
    owner="ingestor",
    contactEmail="scicatingestor@your.site",
    creationLocation="magrathea",
    creationTime=str(datetime.now().isoformat()),
    instrumentId="earth",
    proposalId="deepthought",
    dataFormat="planet",
    type=DatasetType.raw,
    principalInvestigator="admin",
    sourceFolder="/foo/bar",
    scientificMetadata={"a": "field"},
    sampleId="gargleblaster",
    **ownable.model_dump(),
)
dataset_id = client.datasets_create(dataset)

sample = Sample(
    sampleId="gargleblaster",
    owner="Chamber of Commerce",
    description="A legendary drink.",
    sampleCharacteristics={"Flavour": "Unknown, but potent"},
    isPublished=False,
    **ownable.model_dump()
)
sample_id = client.samples_create(sample)
```

### Notes

To develop with SciCatLive, connect to your local running instance with:

```python
client = ScicatClient(base_url="http://localhost/api/v3", username="admin", password="2jf70TPNZsS", auto_login=False)
client._headers["Host"] = "backend.localhost"
client.login()
```

Then use the client normally.