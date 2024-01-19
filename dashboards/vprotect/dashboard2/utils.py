def project_uuid_removal(url):
    return re.sub(r'&?project-uuid=[^&]*', '', url)