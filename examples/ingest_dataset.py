from datetime import datetime
from pathlib import Path

from pyscicat.client import ScicatClient, encode_thumbnail
from pyscicat.model import (
    Attachment,
    CreateDatasetOrigDatablockDto,
    DataFile,
    DatasetType,
    Ownable,
    RawDataset,
)

# Create a client object. The account used should have the ingestor role in SciCat
scicat = ScicatClient(
    base_url="http://localhost:3000/api/v3", username="Zaphod", password="heartofgold"
)

# Create an Ownable that will get reused for several other Model objects
ownable = Ownable(ownerGroup="magrathea", accessGroups=["deep_thought"])
thumb_path = Path(__file__).parent.parent / "test/data/SciCatLogo.png"


# Create a RawDataset object with settings for your choosing. Notice how
# we pass the `ownable` instance.
dataset = RawDataset(
    size=42,
    owner="slartibartfast",
    contactEmail="slartibartfast@magrathea.org",
    creationLocation="magrathea",
    creationTime=str(datetime.now().isoformat()),
    type=DatasetType.raw,
    instrumentId="earth",
    proposalId="deepthought",
    dataFormat="planet",
    datasetName="Douglas' Dataset",
    principalInvestigator="A. Mouse",
    sourceFolder="/foo/bar",
    scientificMetadata={"a": "field"},
    sampleId="gargleblaster",
    **ownable.model_dump(),
)
dataset_id = scicat.datasets_create(dataset)

# Create Datablock with DataFiles
data_file = DataFile(path="file.h5", size=42)
data_block = CreateDatasetOrigDatablockDto(
    size=42,
    dataFileList=[data_file],
    **ownable.model_dump(),
)
scicat.datasets_origdatablock_create(dataset_id, data_block)

# Create Attachment
attachment = Attachment(
    datasetId=dataset_id,
    thumbnail=encode_thumbnail(thumb_path),
    caption="scattering image",
    **ownable.model_dump(),
)
scicat.upload_attachment(attachment)
