import enum

# from re import L
from typing import List, Dict, Optional

from pydantic import BaseModel
from pydantic._internal._model_construction import ModelMetaclass

# creates update models where all the fields are optional
# Might want to consider alternative approaches for better maintainability:
# https://github.com/pydantic/pydantic/issues/6381


class _AllOptional(ModelMetaclass):
    def __new__(self, name, bases, namespaces, **kwargs):
        annotations = namespaces.get('__annotations__', {})

        for base in bases:
            # annotations.update(base.__annotations__)
            for base_ in base.__mro__:
                if base_ is BaseModel:
                    break

                annotations.update(base_.__annotations__)

        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = Optional[annotations[field]]
        namespaces['__annotations__'] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)


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
    email: str
    pi_email: Optional[str] = None
    pi_firstname: Optional[str] = None
    pi_lastname: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    title: Optional[str] = None  # required in next backend version
    abstract: Optional[str] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    MeasurementPeriodList: Optional[
        List[dict]
    ] = None  # may need updating with the measurement period model


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


class Job(MongoQueryable):
    """
    This collection keeps information about jobs to be excuted in external systems.
    In particular it keeps information about the jobs submitted for archiving or
    retrieving datasets stored inside an archive system. It can also be used to keep
    track of analysis jobs e.g. for automated analysis workflows
    """

    emailJobInitiator: str
    type: str
    id: Optional[str] = None
    creationTime: Optional[str] = None  # not sure yet which ones are optional or not.
    executionTime: Optional[str] = None
    jobParams: Optional[dict] = None
    jobStatusMessage: Optional[str] = None
    datasetList: Optional[dict] = None  # documentation says dict, but should maybe be list?
    jobResultObject: Optional[dict] = None  # ibid.


class Instrument(MongoQueryable):
    """
    Instrument class, most of this is flexibly definable in customMetadata
    """

    uniqueName: str
    name: str
    pid: Optional[str] = None
    customMetadata: Optional[dict] = None


class Dataset(Ownable):
    """
    A dataset in SciCat, base class for derived and raw datasets
    """

    contactEmail: str
    creationTime: str  # datetime
    owner: str
    sourceFolder: str
    type: DatasetType
    pid: Optional[str] = None
    classification: Optional[str] = None
    datasetName: Optional[str] = None
    description: Optional[str] = None
    history: Optional[List[dict]] = None  # list of foreigh key ids to the Messages table
    instrumentId: Optional[str] = None
    isPublished: Optional[bool] = False
    keywords: Optional[List[str]] = None
    license: Optional[str] = None
    numberOfFiles: Optional[int] = None
    numberOfFilesArchived: Optional[int] = None
    orcidOfOwner: Optional[str] = None
    packedSize: Optional[int] = None
    ownerEmail: Optional[str] = None
    sharedWith: Optional[List[str]] = None
    size: Optional[int] = None
    sourceFolderHost: Optional[str] = None
    techniques: Optional[List[dict]] = None  # with {'pid':pid, 'name': name} as entries
    validationStatus: Optional[str] = None
    version: Optional[str] = None
    scientificMetadata: Optional[Dict] = None


class UpdateDataset(Dataset, metaclass=_AllOptional):
    pass


class RawDataset(Dataset):
    """
    Raw datasets from which derived datasets are... derived.
    """

    type: DatasetType = DatasetType.raw
    principalInvestigator: Optional[str] = None
    creationLocation: Optional[str] = None
    dataFormat: Optional[str] = None
    endTime: Optional[str] = None  # datetime
    sampleId: Optional[str] = None
    proposalId: Optional[str] = None


class UpdateRawDataset(Dataset, metaclass=_AllOptional):
    pass


class DerivedDataset(Dataset):
    """
    Derived datasets which have been generated based on one or more raw datasets
    """

    investigator: str
    inputDatasets: List[str]
    usedSoftware: List[str]
    type: DatasetType = DatasetType.derived
    jobParameters: Optional[dict] = None
    jobLogData: Optional[str] = None


class UpdateDerivedDataset(DerivedDataset, metaclass=_AllOptional):
    pass


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

    # archiveId: str = None  listed in catamel model, but comes back invalid?
    size: int
    version: str = None
    dataFileList: List[DataFile]
    datasetId: str
    id: Optional[str] = None
    packedSize: Optional[int] = None
    chkAlg: Optional[int] = None
    instrumentGroup: Optional[str] = None


class OrigDatablock(Ownable):
    """
    An Original Datablock maps between a Dataset and contains DataFiles
    """

    size: int
    chkAlg: str
    dataFileList: List[DataFile]
    datasetId: str
    id: Optional[str] = None
    # archiveId: str = None  listed in catamel model, but comes back invalid?


class Attachment(Ownable):
    """
    Attachments can be any base64 encoded string...thumbnails are attachments
    """

    thumbnail: str
    datasetId: str
    id: Optional[str] = None
    caption: Optional[str] = None


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
    abstract: str
    dataDescription: str
    resourceType: str
    pidArray: List[str]
    authors: List[str]
    registeredTime: str
    status: str
    createdBy: str
    updatedBy: str
    createdAt: str
    updatedAt: str
    url: Optional[str] = None
    numberOfFiles: Optional[int] = None
    sizeOfArchive: Optional[int] = None
    thumbnail: Optional[str] = None
