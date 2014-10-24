"""Model class for the sandman2 application."""

# Standard library imports
from decimal import Decimal

# Third-party imports
from sqlalchemy.inspection import inspect
from flask.ext.sqlalchemy import SQLAlchemy  # pylint: disable=import-error,no-name-in-module

db = SQLAlchemy()


class Model(object):
    """The sandman2 Model class is the base class for all RESTful resources.
    There is a one-to-one mapping between a table in the database and a
    :class:`sandman2.model.Model`.

    Attributes:
        __url__: The relative URL this resource should live at
        __version__: The API version of this resource (not yet used)
        __methods__: The HTTP methods this resource supports (default=all)

    Class Methods:
        required: Returns a list of all fields required to create the resource
        optional: Returns a list of additional fields (not required) that may be
                  set on the resource

    Methods:
        primary_key: Returns the name of the resource's primary key field
        to_dict: Returns a dictionary representation of the resource
        links: Return a dictionary of HTTP Link header values
        resource_uri: Return the relative URI to the given instance
        update: Update the fields of the instance with those in the given
                dictionary
    """

    #: The relative URL this resource should live at
    __url__ = None

    #: The API version of this resource (not yet used)
    __version__ = '1'

    #: The HTTP methods this resource supports (default=all)
    __methods__ = set([
        'GET',
        'POST',
        'PUT',
        'PATCH',
        'DELETE',
        'HEAD',
        'OPTIONS'])

    @classmethod
    def required(cls):
        """Return a list of all columns required by the database to create the
        resource.

        :param cls: The Model class to gather attributes from
        :rtype list:
        """
        columns = []
        for column in cls.__table__.columns:  # pylint: disable=no-member
            if not column.nullable and not column.primary_key:
                columns.append(column.name)
        return columns

    @classmethod
    def optional(cls):
        """Return a list of all nullable columns for the resource's table.

        :param cls: The Model class to gather attributes from
        :rtype list:
        """
        columns = []
        for column in cls.__table__.columns:  # pylint: disable=no-member
            if column.nullable:
                columns.append(column.name)
        return columns

    def primary_key(self):
        """Return the name of the model's primary key field.
        
        :rtype str:
        """
        return list(
            self.__table__.primary_key.columns)[  # pylint: disable=no-member
                0].name

    def to_dict(self):
        """Return the resource as a dictionary.

        :rtype dict:
        """
        result_dict = {}
        for column in self.__table__.columns.keys():  # pylint: disable=no-member
            value = result_dict[column] = getattr(self, column, None)
            if isinstance(value, Decimal):
                result_dict[column] = float(result_dict[column])
        return result_dict

    def links(self):
        """Return a dictionary of links to related resources that should be
        included in the *Link* header of an HTTP response.

        :rtype dict:
        """
        link_dict = {'self': self.resource_uri()}
        for relationship in inspect(self.__class__).relationships:  # pylint: disable=maybe-no-member
            if 'collection' not in relationship.key:
                instance = getattr(self, relationship.key)
                if instance:
                    link_dict[str(relationship.key)] = instance.resource_uri()
        return link_dict

    def resource_uri(self):
        """Return the URI to this specific resource.

        :rtype str:
        """
        return self.__url__ + '/' + str(getattr(self, self.primary_key()))

    def update(self, attributes):
        """Update the current instance based on attribute->value items in
        *attributes*.

        :param dict attributes: Dictionary of attributes to be updated
        :rtype :class:`sandman2.model.Model` :
        """
        for attribute in attributes:
            setattr(self, attribute, attributes[attribute])
        return self