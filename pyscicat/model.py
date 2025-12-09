import enum

# from re import L
from typing import Dict, List, Optional

from pydantic import BaseModel


class DatasetType(str, enum.Enum):
    """type of Dataset"""

    raw = "raw"
    derived = "derived"


class MongoQueryable(BaseModel):
    """Many objects in SciCat are mongo queryable"""

    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    updatedAt: Optional[str] = None
    createdAt: Optional[str] = None


class Ownable(MongoQueryable):
    """Many objects in SciCat are ownable"""

    ownerGroup: str
    accessGroups: Optional[List[str]] = None
    instrumentGroup: Optional[str] = None


class User(BaseModel):
    """Base user."""

    # TODO: find out which of these are not optional and update
    realm: str
    username: str
    email: str
    emailVerified: bool = False
    id: str


class Proposal(Ownable):
    """
    Defines the purpose of an experiment and links an experiment to principal investigator and main proposer
    """

    proposalId: str
    pi_email: Optional[str] = None
    pi_firstname: Optional[str] = None
    pi_lastname: Optional[str] = None
    email: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    title: Optional[str] = None  # required in next backend version
    abstract: Optional[str] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    MeasurementPeriodList: Optional[List[dict]] = (
        None  # may need updating with the measurement period model
    )


class Sample(Ownable):
    """
    Models describing the characteristics of the samples to be investigated.
    Raw datasets should be linked to such sample definitions.
    """

    sampleId: Optional[str] = None
    owner: Optional[str] = None
    description: Optional[str] = None
    sampleCharacteristics: Optional[dict] = None
    isPublished: bool = False
    datasetsId: Optional[str] = None
    datasetId: Optional[str] = None
    rawDatasetId: Optional[str] = None
    derivedDatasetId: Optional[str] = None


class Job(MongoQueryable):
    """
    This collection keeps information about jobs to be excuted in external systems.
    In particular it keeps information about the jobs submitted for archiving or
    retrieving datasets stored inside an archive system. It can also be used to keep
    track of analysis jobs e.g. for automated analysis workflows
    """

    id: Optional[str] = None
    emailJobInitiator: str
    type: str
    creationTime: Optional[str] = None  # not sure yet which ones are optional or not.
    executionTime: Optional[str] = None
    jobParams: Optional[dict] = None
    jobStatusMessage: Optional[str] = None
    datasetList: Optional[dict] = (
        None  # documentation says dict, but should maybe be list?
    )
    jobResultObject: Optional[dict] = None  # ibid.


class Instrument(MongoQueryable):
    """
    Instrument class, most of this is flexibly definable in customMetadata
    """

    pid: Optional[str] = None
    name: str
    uniqueName: str
    customMetadata: Optional[dict] = None


class RelationshipClass(BaseModel):
    """
    Decscribes a relationship between datasets
    """

    pid: str
    relationship: str


class DatasetLifeCycleClass(BaseModel):
    """
    Describes the lifecycle of a dataset
    """

    archivable: Optional[str] = None
    archiveRetentionTime: Optional[str] = None  # datetime
    archiveReturnMessage: Optional[dict] = None
    archiveStatusMessage: Optional[str] = None
    dateOfDiskPurging: Optional[str] = None  # datetime
    dateOfPublishing: Optional[str] = None  # datetime
    exportedTo: Optional[str] = None
    isOnCentralDisk: Optional[str] = None
    publishable: Optional[str] = None
    publishedOn: Optional[str] = None  # datetime
    retrievable: Optional[str] = None
    retrieveReturnMessage: Optional[dict] = None
    retrieveStatusMessage: Optional[str] = None
    retrieveIntegrityCheck: Optional[str] = None
    storageLocation: Optional[str] = None


class DatasetCommon(Ownable):
    """
    The common fields in a standard DataSet, a RawDataset, and a DerivedDataset
    """

    pid: Optional[str] = None
    classification: Optional[str] = None
    comment: Optional[str] = None
    contactEmail: str
    creationTime: str  # datetime
    datasetName: str
    datasetlifecycle: Optional[DatasetLifeCycleClass] = None
    dataQualityMetrics: Optional[int] = None
    description: Optional[str] = None
    history: Optional[List[dict]] = (
        None  # list of foreign key ids to the Messages table
    )
    instrumentId: Optional[str] = None
    investigator: Optional[str] = None
    isPublished: Optional[bool] = False
    jobLogData: Optional[str] = None
    jobParameters: Optional[dict] = None
    keywords: Optional[List[str]] = None
    license: Optional[str] = None
    numberOfFiles: Optional[int] = None
    numberOfFilesArchived: Optional[int] = None
    orcidOfOwner: Optional[str] = None
    ownerEmail: Optional[str] = None
    packedSize: Optional[int] = None
    relationships: Optional[List[RelationshipClass]] = None
    runNumber: Optional[str] = None
    scientificMetadata: Optional[Dict] = None
    sharedWith: Optional[List[str]] = None
    size: Optional[int] = None
    sourceFolder: str
    sourceFolderHost: Optional[str] = None
    techniques: Optional[List[dict]] = None  # with {'pid':pid, 'name': name} as entries
    validationStatus: Optional[str] = None
    version: Optional[str] = None


class Dataset(DatasetCommon):
    """
    A dataset in SciCat, base class for derived and raw datasets
    """

    creationLocation: Optional[str] = None  # Optional for a standard dataset
    dataFormat: Optional[str] = None
    endTime: Optional[str] = None  # datetime
    inputDatasets: Optional[List[str]] = None
    owner: Optional[str] = None
    principalInvestigators: Optional[List[str]] = None
    proposalIds: Optional[List[str]] = None
    sampleIds: Optional[List[str]] = None
    scientificMetadataSchema: Optional[str] = None
    type: DatasetType
    usedSoftware: Optional[List[str]] = None


class RawDataset(DatasetCommon):
    """
    Raw datasets from which derived datasets are... derived.
    """

    creationLocation: str  # Required for a raw dataset
    dataFormat: Optional[str] = None
    endTime: Optional[str] = None  # datetime
    inputDatasets: Optional[List[str]] = None
    owner: str
    principalInvestigator: str  # Required for a raw dataset
    proposalId: Optional[str] = None
    sampleId: Optional[str] = None
    type: DatasetType = DatasetType.raw
    usedSoftware: Optional[List[str]] = None


class DerivedDataset(DatasetCommon):
    """
    Derived datasets which have been generated based on one or more raw datasets
    """

    inputDatasets: List[str] = []
    owner: str
    proposalId: Optional[str] = None
    type: DatasetType = DatasetType.derived
    usedSoftware: List[str] = []


class DatasetUpdateDto(DatasetCommon):
    """
    A dataset in the form sent to the update APIs, where almost everything is optional
    """

    contactEmail: Optional[str] = None
    creationTime: Optional[str] = None  # datetime
    creationLocation: Optional[str] = None
    dataFormat: Optional[str] = None
    datasetName: Optional[str] = None
    endTime: Optional[str] = None  # datetime
    inputDatasets: Optional[List[str]] = None
    owner: Optional[str] = None
    principalInvestigator: Optional[str] = None
    proposalId: Optional[str] = None
    sampleId: Optional[str] = None
    sourceFolder: Optional[str] = None
    type: Optional[DatasetType] = None
    usedSoftware: Optional[List[str]] = None


class DataFile(MongoQueryable):
    """
    A reference to a file in SciCat. Path is relative
    to the Dataset's sourceFolder parameter

    """

    path: str
    size: int
    time: Optional[str] = None
    chk: Optional[str] = None
    uid: Optional[str] = None
    gid: Optional[str] = None
    perm: Optional[str] = None


class Datablock(Ownable):
    """
    A Datablock maps between a Dataset and contains DataFiles
    """

    id: Optional[str] = None
    archiveId: Optional[str] = None
    size: Optional[int] = None
    packedSize: Optional[int] = None
    chkAlg: Optional[str] = None
    version: str
    dataFileList: List[DataFile]
    datasetId: str


class CreateDatasetOrigDatablockDto(BaseModel):
    """
    DTO for creating a new dataset with an original datablock
    """

    size: int
    chkAlg: Optional[str] = None
    dataFileList: List[DataFile]


class OrigDatablock(Ownable, CreateDatasetOrigDatablockDto):
    """
    An Original Datablock maps between a Dataset and contains DataFiles
    """

    id: Optional[str] = None
    datasetId: str


class Attachment(Ownable):
    """
    Attachments can be any base64 encoded string...thumbnails are attachments
    They can be associated with proposals, samples, or datasets.
    """

    id: Optional[str] = None
    datasetId: Optional[str] = None
    proposalId: Optional[str] = None
    sampleId: Optional[str] = None
    thumbnail: Optional[str] = None
    caption: str


class PublishedData:
    """
    Published Data with registered DOI
    """

    doi: str
    affiliation: str
    creator: List[str]
    publisher: str
    publicationYear: int
    title: str
    url: Optional[str] = None
    abstract: str
    dataDescription: str
    resourceType: str
    numberOfFiles: Optional[int] = None
    sizeOfArchive: Optional[int] = None
    pidArray: List[str]
    authors: List[str]
    registeredTime: str
    status: str
    thumbnail: Optional[str] = None
    createdBy: str
    updatedBy: str
    createdAt: str
    updatedAt: str
