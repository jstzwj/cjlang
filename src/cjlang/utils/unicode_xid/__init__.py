from .tables import XID_Continue, XID_Start


def is_xid_start(char: str) -> bool:
    # Fast-path for ascii idents
    return (
        ("a" <= char <= "z")
        or ("A" <= char <= "Z")
        or (char > "\x7f" and XID_Start(char))
    )


def is_xid_continue(char: str) -> bool:
    # Fast-path for ascii idents
    return (
        ("a" <= char <= "z")
        or ("A" <= char <= "Z")
        or ("0" <= char <= "9")
        or char == "_"
        or (char > "\x7f" and XID_Continue(char))
    )
