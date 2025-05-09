# Scicat Ingesting Guide
Here we provide some tips for getting started in ingesting data into SciCat. It is assumed that the reader has a working knowledge of [JSON](https://restfulapi.net/introduction-to-json/) and [REST](https://restfulapi.net/).

<i>What is ingestion?</i> 

We define `ingestion` as meaning reading datasets from their native format on disk (or database), extracting metadata and sending it to SciCat. Scicat stores information about users, datasets, proposals, etc. in collections in a MongoDB instance. For each collection, there a combination of required and optional fields, which present choices that the ingestion developer to make. See the [official scicat documentaiton](https://scicatproject.github.io/documentation/Development/Data_Model.html) for an exhaustive description of the data model. We do not reproduce the data model here, but make references to it with suggestions on how to use it when ingesting metadata.

Again, SciCat does not store data files directly. It contains references to data set files on a file system (available to the web server). Part of the ingestion process involves what to extract to enter into the database how how to represent it.

## Technical Details
All ingestion is done using the [Scicat API](https://scicatproject.github.io/api/), which is a RESTful interface. Before you can ingest, you must be assigned a username/password combination by your Scicat administrator. 

This project contains an [Ingestor class](../scicat_ingestor/ingestor.py) and model classes (Dataset, Datablock, Datafile, etc) for carrying and validating the objects send to Scicat. The list of classes is not exhaustive, and will surely grow over time. For a relatively simple example of how they can be used, [see](../scicat_ingestor/jobs/als_11012_ccd_theta.py). 


### Authorization
Many of the classes (Dataset, Datablock, etc.) are "Ownable", containing fields `accessGroups` and `ownerGroup`. When users login, they are assigned a list of accessGroups depending from external systems (suchs a User Office system or AD/LDAP system). A user's `groups` are compared to the object's `accessGroups` and `ownerGroup` to determine whether the user can see and/or modify the object.

#### accessGroups
A list of groups tagged in an object (e.g. Dataset). If one of the user's `groups` matches one of the object's `accessGroups`, the user will be able to see the object in the system, and it will appear in search results.

#### ownerGroup
A single group tagged in an object (e.g. Dataset). If one of the user's `accessGroups` matches one of the object's `ownerGroup`, the user will be able to see AND edit the object...though not all fields of an object are editable.

## Scientific Metadata and Sample Characteristics
Several of the following examples reference `Scientific Metadata` and `Sample Characteristics`. These  free form dictionaries (or in JSON terms, objects) are displayed in Scicat alongside the enclosing objects (`Dataset` and `Sample`). Since these fields are free-form, care should be taken when designing the structure of these objects.

## Tools and utilities for importing HDF5/NeXus files

A few tools and utilities are available for handling and uploading structured HDF5 files, 
including those defined by the NeXus working group. 

Methods `h5Get` and `h5GetDict` in `h5tools` can be used to easily extract a single piece of metadata or a group of metadata entries from an HDF5 file. These methods have error hancling and default handling. 

Moreover, an automated method `scientific_metadata` is available with the HDF5 tools accompanying pyscicat. This method reads the entire tree from an HDF5 file structure,
and converts this to a dictionary of keys, values and units that can be used directly to 
populate the scientific metadata field. 

# Examples

## Document Conventions
This document contains examples of the data that one would send to SciCat during the ingestion process. We use JSON notation as it is common and easy to read. These examples will always include required fields, but, for brevity, will often omit optional fields. In many cases, these documents relate to each other using ID fields. These fields are always generated on the server and returned when a new object is created. They are generally large random strings. For clarity, the examples in this document will adopt convention to express these ids similar `<<datasetId-1>>`, in order to make it easy to follow them in the examples.

## Minimal Task - Raw Dataset
Perhaps the fundamental Scicat ingestion task is ingesting [Raw Datasets](https://scicatproject.github.io/documentation/Development/Data_Model.html#rawdataset). `RawDataset` object represents the data taken directly from an instrument. When ingested, Scicat will display to the user:
* ownership information
* tracking information about times and dates
* [Scientific Metadata](scientific_metadata)
* (optionally) a folder in a storage system where the `Dataset` files can be found
* (optionally) a list of the dataset's files that can be downloaded through Scicat.

Before ingesting a dataset, a few decisions have to be made:

* Where do the files themselves live? The `Dataset.sourcesFolder` field is required and it represents the folder into which all of the `Dataset` files live. In order for the Download feature to work, this folder must be available to the Scicat `zip-service` instance.
* What is the sample? In the SciCat `Dataset` schema, `sampleID` is a required field. This means that before ingesting the `Dataset`, a valid `Sample` must be ingested.
* What fields to add to `ownerGroup` and `accessGroups`? These fields are going to be required for several of the create messages sent to SciCat.

First, send a POST request to the [Sample endpoint](https://scicatproject.github.io/api/#operation/Sample.create). 

Similar to [Scientific Metadata](scientific_metadata), the `Sample` object contains a free-form object called `sampleCharacteristics` in which one can add properties of the sample.

### Ingest Sample
`Sample` sample object
``` json

{

    "owner": "Beamline User",
    "description": "Descriptive sample information",
    "createdAt": "2019-08-24T14:15:22Z",
    "sampleCharacteristics": { },
    "isPublished": false,
    "ownerGroup": "ProposalGroup-1",
    "accessGroups": 

    [
        "ProposalGroup-1",
        "BeamlineGroups-1"
    ],
    "updatedAt": "2019-08-24T14:15:22Z",
    "sampleCharacteristics": {
        
    }
}
```
A successful response to this message will contain a `sampleId` field that will be used when creating related `Datasets`

Next, send a POST request to the [Dataset endpoint](https://scicatproject.github.io/api/#operation/Dataset.create)

### Ingest Dataset
`RawDataset` sample object
``` json

{

    "sampleId": <<sampleId_1>>,
    "owner": "Beamline User",
    "description": "A data set taken by beamline user",
    "createdAt": "2019-08-24T14:15:22Z",
    "contactEmail": "person@example.com",
    "creationLocation": "beamline1",
    
    "creationTime": "2019-08-24T14:15:22Z",
    "instrumentId": "beamline1",
    "proposalId": "proposal1",
    "dataFormat": "nexus",
    "principalInvestigator": "A. Scientist",
    "sourceFolder": "/a/b/c/d",
    "isPublished": false,
    "ownerGroup": "ProposalGroup-1",
    "accessGroups": 

    [
        "ProposalGroup-1",
        "BeamlineGroups-1"
    ],
    "updatedAt": "2019-08-24T14:15:22Z"

}

```

One other very interesting field that can be added to `Datasets` is `keywords`. This is a list of strings that can be used to provide very useful search filters in the SciCat search tool. 

Another thing to note about datasets is the `sourceFolder` field. This is set to the base directory where all files for the `Dataset` are located. Individual file names within that folder are set in `Datafile` objects, described next.

### Ingest Datablocks and Datafiles
In Scicat, the ability to view and download the files for a `Dataset` depends on ingesting a `Datablock`, which contains one zero or more 'Datafile' instances. 

```json

{

    "archiveId": "uniqueId",
    "size": 100000,

    "version": null,
    "dataFileList": 

[

    {"path": "file1.txt", "size": "1000"},
    {"path": "file2.nxs", "size": "10000000"}

],
"ownerGroup": "string",
    "accessGroups": 

    [
        "ProposalGroup-1",
        "BeamlineGroups-1"
    ],
"createdBy": "string",
"updatedBy": "string",
"datasetId": "string",
"rawDatasetId": "string",
"derivedDatasetId": "string",
"createdAt": "2019-08-24T14:15:22Z",
"updatedAt": "2019-08-24T14:15:22Z"

}

```

### Dataset generation with HDF5 tools examples

In the following example, h5Get and scientific_metadata are used to:
  - get a single attribute from the HDF5 file, or default to the current timestamp, and
  - Construct the scientific metadata tree, while excluding huge data entries by their key. 

```python

from pyscicat.hdf5.scientific_metadata import scientific_metadata
from pyscicat.hdf5.h5tools import h5Get
from datetime import datetime
from patlib import Path

filePath = Path('SPONGE/simData/cylArray_h100_r4_d12_n15.nxs')
modTime = get_file_mod_time(filePath)
fileSize = get_file_size(filePath)

# rawDataset
dataset = RawDataset(
    path = filePath.as_posix(),
    size = fileSize,
    owner = 'Sponge',
    contactEmail = 'example@bam.de',
    creationLocation = "UE H30 Ingo's server",
    creationTime = h5Get(filePath, '/sasentry1/sasdata1@timestamp', default=str(datetime.utcnow().isoformat()[:-3]+'Z')),
    type = 'raw',
    instrumentId='BAM:Sponge',
    proposalId='2021001',
    sampleId='2021001-1',
    dataFormat='NeXus',
    principalInvestigator='tester',
    sourceFolder=filePath.parent.as_posix(),
    scientificMetadata=scientific_metadata(filePath, skipKeyList=['simulationMetaValues', 'simData', 'surfaceAreas']),
    ownerGroup="Sponge", 
    accessGroups=["sponge", "testGroup"]
)
```

## Finding, modifying and/or deleting datasets

## Additional Tasks
[TBD]

### Samples

### Derived Datasets

### Proposals

### Instruments

### Logbooks

### Jobs

## Techniques


