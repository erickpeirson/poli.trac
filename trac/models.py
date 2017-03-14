from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, Time, Text
from sqlalchemy.orm import relationship
from trac.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(120), unique=True)

    def __init__(self, username=None, email=None):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username


class Politician(Base):
    __tablename__ = 'politician'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    website = Column(String(255))

    HOUSE = 'HO'
    SENATE = 'SE'
    CHAMBERS = (
        (HOUSE, 'House'),
        (SENATE, 'Senate'),
    )

    chamber = Column(String(2), nullable=False)

    sponsored_bills = relationship('Sponsorship', back_populates='politician')
    committees = relationship('CommitteeMembership', back_populates='politician')


class BillSubject(Base):
    __tablename__ = 'bill_subject'
    bill_id = Column(Integer, ForeignKey('bill.id'), primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'), primary_key=True)

    PRIMARY = "PRI"
    SECONDARY = "SEC"
    status = Column(String(3), nullable=False)

    bill = relationship("Bill", back_populates="subjects")
    subject = relationship("Subject", back_populates="bills")


class Sponsorship(Base):
    __tablename__ = 'sponsorship'
    politician_id = Column(Integer, ForeignKey('politician.id'), primary_key=True)
    bill_id = Column(Integer, ForeignKey('bill.id'), primary_key=True)

    date = Column(Date)
    date_withdrawn = Column(Date)
    is_original = Column(Boolean)

    politician = relationship("Politician", back_populates="sponsored_bills")
    bill = relationship("Bill", back_populates="sponsors")


class CommitteeMembership(Base):
    __tablename__ = 'committee_membership'
    committee_id = Column(String(6), ForeignKey('committee.code'), primary_key=True)
    politician_id = Column(Integer, ForeignKey('politician.id'), primary_key=True)

    committee = relationship("Committee", back_populates="members")
    politician = relationship("Politician", back_populates="committees")


class Subject(Base):
    """

    > Legislative subject terms like those found in describe a measure's
    > substance and effects. There are approximately 1,000 issue-oriented,
    > entity, and geographic terms.

    https://github.com/usgpo/bill-status/blob/master/BILLSTATUS-XML_User_User-Guide.md
    """

    __tablename__ = 'subject'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    parent_id = Column(Integer, ForeignKey('subject.id'))
    children = relationship("Subject")

    bills = relationship('BillSubject', back_populates='subject')


class Bill(Base):
    __tablename__ = 'bill'

    id = Column(Integer, primary_key=True)
    introduced = Column(Date, nullable=False)
    congress = Column(Integer)
    number = Column(Integer)
    title = Column(String(1000), nullable=False)

    HOUSE = 'H'
    SENATE = 'S'
    HOUSE_RESOLUTION = 'HRES'
    SENATE_RESOLUTION = 'SRES'
    HOUSE_JOINT_RESOLUTION = 'HJRES'
    SENATE_JOINT_RESOLUTION = 'SJRES'
    HOUSE_CONCURRENT_RESOLUTION = 'HCONRES'
    SENATE_CONCURRENT_RESOLUTION = 'SCONRES'
    BILL_TYPES = (
        (HOUSE, 'House bill'),
        (SENATE, 'Senate bill'),
        (HOUSE_RESOLUTION, 'House resolution'),
        (SENATE_RESOLUTION, 'Senate resolution'),
        (HOUSE_JOINT_RESOLUTION, 'House joint resolution'),
        (SENATE_JOINT_RESOLUTION, 'Senate joint resolution'),
        (HOUSE_CONCURRENT_RESOLUTION, 'House concurrent resolution'),
        (SENATE_CONCURRENT_RESOLUTION, 'Senate concurrent resolution'),
    )
    bill_types = Column(String(7), nullable=False)

    HOUSE = 'HO'
    SENATE = 'SE'
    CHAMBERS = (
        (HOUSE, 'House'),
        (SENATE, 'Senate'),
    )
    origin_chamber = Column(String(2), nullable=False)

    subjects = relationship('BillSubject', back_populates='bill')
    sponsors = relationship('Sponsorship', back_populates='bill')
    actions = relationship('Action', back_populates='bill')
    amendments = relationship("Amendment", back_populates='bill')


# TODO: support amendments to amendments.
class Amendment(Base):
    __tablename__ = 'amendment'
    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey('bill.id'))
    bill = relationship("Bill", back_populates='amendments')

    amendment_type = Column(String(200))
    number = Column(Integer)
    description = Column(Text)
    purpose = Column(Text)


class Committee(Base):
    __tablename__ = 'committee'
    code = Column(String(6), primary_key=True)
    name = Column(String(400))
    members = relationship('CommitteeMembership', back_populates='committee')

    HOUSE = 'HO'
    SENATE = 'SE'
    CHAMBERS = (
        (HOUSE, 'House'),
        (SENATE, 'Senate'),
    )
    chamber = Column(String(2), nullable=False)

    subcommittees = relationship('Committee', back_populates='parent')

    parent_code = Column(String(6), ForeignKey('committee.code'))
    parent = relationship('Committee', back_populates='subcommittees', remote_side=code)

    actions = relationship('Action', back_populates='committee')


class Action(Base):
    __tablename__ = 'action'

    ACTION_CODES = [
        ("B00100", "Sponsor introductory remarks on measure"),
        ("E20000", "Presented to President"),
        ("E30000", "Signed by President"),
        ("E40000", "Became Public Law No: 114-47"),
        ("H11100", "Referred to the Committee"),
        ("H11200", "Sequential committee referral"),
        ("H12100", "Committee report of an original measure"),
        ("H12200", "Committee reported"),
        ("H12300", "Committee discharged"),
        ("H12410", "Union Calendar assignment"),
        ("H14000", "Received in the House"),
        ("H15000", "Held at the desk"),
        ("H17000", "Motion to Discharge Committee"),
        ("H1L210", "Rule provides for consideration of"),
        ("H25200", "Conference report [free text] filed"),
        ("H37300", "Final Passage Under Suspension of the Rules Results"),
        ("H38310", "Motion To Reconsider Results"),
        ("H30000", "Consideration by House"),
        ("H8D000", "DEBATE"),
        ("H81000", "Point of order against a motion"),
        ("1000", "Introduced in House"),
        ("2000", "Referred to House committee"),
        ("5000", "Reported to House"),
        ("8000", "Passed/agreed to in House"),
        ("10000", "Introduced in Senate"),
        ("11000", "Referred to Senate committee"),
        ("13100", "Senate committee/subcommittee hearings"),
        ("13200", "Senate committee/subcommittee markups"),
        ("14000", "Reported to Senate"),
        ("14500", "Senate committee discharged"),
        ("14900", "Senate committee report filed after reporting"),
        ("17000", "Passed/agreed to in Senate"),
        ("28000", "Presented to President."),
        ("36000", "Became Public Law"),
    ]

    id = Column(Integer, primary_key=True)
    action_code = Column(String(6), nullable=False)
    action_date = Column(Date)
    action_time = Column(Time)

    bill_id = Column(Integer, ForeignKey('bill.id'))
    bill = relationship("Bill", back_populates='actions')

    committee_id = Column(String(6), ForeignKey('committee.code'))
    committee = relationship('Committee', back_populates='actions')

    text = Column(Text)
    source_system_code = Column(Integer)
    source_system_name = Column(String(20))
    action_type = Column(String(100))
    """
    > Action types primarily represents legislative process stages or categories
    > of more detailed actions. Most types condense actions into sets. Some
    > types are used for data processing and do not represent House or Senate
    > legislative process activities.

    https://github.com/usgpo/bill-status/blob/master/BILLSTATUS-XML_User_User-Guide.md
    """
