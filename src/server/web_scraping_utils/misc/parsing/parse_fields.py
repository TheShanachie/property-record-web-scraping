# Define the possibly pages that are scraped from the indevidual record site.
pages = ["Parcel",
         "Owner",
         "Multi-Owner",
         "Residential",
         "Commercial",
         "Out Buildings",
         "Land",
         "Values",
         "Homestead",
         "Sales",
         "Tax Information",
         "Photos",
         "Sletch",
         "Map"]

# Preliminary schema for meta data.
heading_schema = {
    # "$id": None,
    # "$schema": None,
    "title:": "heading",
    "type": "object",
    "properties": {
        "PARID": {
            "type": "string",
            "description": "Presumably unique identifier for a property/parcel record."
        },
        "Owner": {
            "type": "string",
            "description": "Name of the owner of the property."
        },
        "Address": {
            "type": "string",
            "description": "Physical address of the property."
        },
    }   
}

# Page data holds the non-metadata information for each page.
full_schema = {}

# Create a JSON Scheme for the relevant proprty page data, scraped from the site.
parcel_schema = {
    "title": "Parcel",
    "type": "object",
    "properties": {
        "Parcel": {
            "type": "object",
            "properties": {
                "Property Location": { "type": "string" },
                "Unit Desc": { "type": "string" },
                "Unit #": { "type": "string" },
                "City": { "type": "string" },
                "State": { "type": "string" },
                "Zip Code": { "type": "string" },
                "Neighborhood Valuation Code": { "type": "string" },
                "Trailer Description": { "type": "string" },
                "Municipality": { "type": "string" },
                "Classification": { "type": "string" },
                "Land Use Code": { "type": "string" },
                "School District": { "type": "string" },
                "Topography": { "type": "string" },
                "Utilities": { "type": "string" },
                "Street/Road": { "type": "string" },
                "Total Cards": { "type": "string" },
                "Living Units": { "type": "string" },
                "CAMA Acres": { "type": "string" },
                "Homestead /Farmstead": { "type": "string" },
                
                "Approved?": { "type": "string" },
                "...": { "type": "string" },
                "...": { "type": "string" },
            }},
        
        "Parcel Mailing Address": {
            "type": "object",
            "properties": {
                "In Care of": { "type": "string" },
                "Name(s)": { "type": "string" },
                "Mailing Address": { "type": "string" },
                "City, State, Zip Code": { "type": "string" },
            }},
        
        "Alternate Address": {
            "type": "object",
            "properties": {
                "Alternate Address": { "type": "string" },
                "City": { "type": "string" },
                "State": { "type": "string" },
                "Zip": { "type": "string" },
            }},
        
        "ACT Flags": {
            "type": "object",
            "properties": {
                "Act 319/515": { "type": "string" },
                "LERTA": { "type": "string" },
                "Act 43": { "type": "string" },
                "Act 66": { "type": "string" },
                "Act 4/149": { "type": "string" },
                "KOZ": { "type": "string" },
                "TIF Expiration Date": { "type": "string" },
                "BID": { "type": "string" },
                "Millage Freeze Date": { "type": "string" },
                "Millage Freeze Rate": { "type": "string" },
                "Veterans Exemption": { "type": "string" },
            }},
    }
}

