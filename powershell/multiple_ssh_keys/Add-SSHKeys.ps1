# Add SSH keys to ssh-agent at startup
$keys = @(
    "C:/Users/EricSzegedi/.ssh/id_rsa",
    "C:/Users/EricSzegedi/.ssh/id_rsa_hpe",
    "C:/Users/EricSzegedi/.ssh/id_ed25519"
)

foreach ($key in $keys) {
    # Check if key is already added
    $list = ssh-add -l 2>$null
    if ($list -notmatch [regex]::Escape($key)) {
        ssh-add $key
    }
}
