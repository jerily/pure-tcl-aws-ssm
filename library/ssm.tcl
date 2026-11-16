# 
# Copyright Jerily LTD. All Rights Reserved.
# SPDX-FileCopyrightText: 2026 Neofytos Dimitriou (neo@jerily.cy)
# SPDX-License-Identifier: MIT.
# 

package require pure-tcl-aws-core 0.1.0
namespace eval ::aws::ssm {namespace path ::aws::core}
::aws::core::register ssm {put_parameter get_parameter delete_parameter}

# Store a parameter, optionally replacing its current value.
proc ::aws::ssm::_put_parameter {client name value {type String} {overwrite false}} {
    if {$type ni {String StringList SecureString}} {error "invalid parameter type"}
    json $client AmazonSSM.PutParameter [dict create Name [list S $name] Value [list S $value] Type [list S $type] Overwrite [list BOOL [boolean $overwrite]]]
    return
}

# Return the legacy name/type/value/version parameter dictionary.
proc ::aws::ssm::_get_parameter {client name {with_decryption false}} {
    set result [json $client AmazonSSM.GetParameter [dict create Name [list S $name] WithDecryption [list BOOL [boolean $with_decryption]]] 1.1 1]
    set p [dict get $result Parameter]
    return [dict create name [dict get $p Name] type [dict get $p Type] value [dict get $p Value] version [dict get $p Version]]
}

# Delete a parameter by name.
proc ::aws::ssm::_delete_parameter {client name} {
    json $client AmazonSSM.DeleteParameter [dict create Name [list S $name]]
    return
}
package provide pure-tcl-aws-ssm 0.1.0
package provide awsssm 1.0.19
