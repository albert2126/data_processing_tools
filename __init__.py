"""
Hierarchy of objects:

*   Content: a set of projects (direction). The whole documentation is about it; so there is no related class
    or object here.

*   Project: an object of this class contains is a container of one project".
    It creates objects related to the project:
    - Job objects
    - A Data object

*   Job: an object of this class represents one job included in its parent project. It requests the related
    PieData object to create a DataSet object representing the output of this job.

*   Data: an object of this class works as a container of all data of one project (class Project). It creates
    DataSet objects.

*   DataSet: an object of this class represent an output of a job and can be consumed by another job.
"""
