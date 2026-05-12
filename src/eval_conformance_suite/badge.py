def badge(framework, passed=True):
    color="green" if passed else "red"
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="220" height="20"><text x="0" y="15">rubric-spec v1: {framework} {"pass" if passed else "fail"}</text><rect x="200" y="0" width="20" height="20" fill="{color}"/></svg>'
