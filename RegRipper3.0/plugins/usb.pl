#-----------------------------------------------------------
# usb
#
# History:
#   20200515 - updated date output format
#   20190819 - updated to include time stamps
#   20141111 - updated check for key LastWrite times
#		20141015 - created
#
# Ref:
#   http://studioshorts.com/blog/2012/10/windows-8-device-property-ids-device-enumeration-pnpobject/
#
# copyright 2020 QAR, LLC
# Author: H. Carvey, keydet89@yahoo.com
#-----------------------------------------------------------
package usb;
use strict;
use utf8;
use Data::Dump;
use Text::CSV;
use Array::Transpose;

my %config = (hive          => "System",
              osmask        => 22,
              hasShortDescr => 1,
              hasDescr      => 0,
              hasRefs       => 0,
              version       => 20200515);

sub getConfig{return %config}

sub getShortDescr {
	return "Get USB key info";	
}
sub getDescr{}
sub getRefs {}
sub getHive {return $config{hive};}
sub getVersion {return $config{version};}

my $VERSION = getVersion();
my @result = (["sub key name", "sub key time", "serial number", "serial number time", "properties key last write", "FrinedlyName", "ParentIdPrefix", "First InstallDate", "InstallDate", "LastArrival", "LastRemoval"],);
my $count = 0;
my $i = 0;
my $flag;

sub pluginmain {
	my $class = shift;
	my $hive = shift;
	::logMsg("Launching usb v.".$VERSION);
	::rptMsg("usb v.".$VERSION); # banner
	::rptMsg("(".getHive().") ".getShortDescr()."\n"); # banner
	my $reg = Parse::Win32Registry->new($hive);
	my $root_key = $reg->get_root_key;

# Code for System file, getting CurrentControlSet
	my $current;
	my $ccs;
	my $key_path = 'Select';
	my $key;
	if ($key = $root_key->get_subkey($key_path)) {
		$current = $key->get_value("Current")->get_data();
		$ccs = "ControlSet00".$current;
	}
	else {
		::rptMsg($key_path." not found.");
		return;
	}

	my $key_path = $ccs."\\Enum\\USB";
	my $key;
	if ($key = $root_key->get_subkey($key_path)) {
		::rptMsg("USBStor");
		::rptMsg($key_path);
		::rptMsg("");
		
		my @subkeys = $key->get_list_of_subkeys();
		if (scalar(@subkeys) > 0) {
			foreach my $s (@subkeys) {
				my @sk = $s->get_list_of_subkeys();
				if (scalar(@sk) > 0) {
					foreach my $k (@sk) {
						my @arrayRow = ();
						#append sub key name
						push(@arrayRow, $s->get_name);
						
						eval{
							#append sub key time
							push(@arrayRow, ::getDateFromEpoch($s->get_timestamp())."Z");
						};
						
						my $serial = $k->get_name();

						#append serial key
						push(@arrayRow, $serial);
						eval{
							#append serial key time
							push(@arrayRow, ::getDateFromEpoch($k->get_timestamp())."Z");
						};
						
						eval {
							#append property key lastwrite
							push(@arrayRow, ::getDateFromEpoch($k->get_subkey("Properties")->get_timestamp())."Z");
						};

						my $friendly;
						eval {
							$friendly = $k->get_value("FriendlyName")->get_data();
						};
						#append friendly name
						push(@arrayRow, $friendly);

						my $parent;
						eval {
							$parent = $k->get_value("ParentIdPrefix")->get_data();
						};
						#append parentIdPrefix
						push(@arrayRow, $parent);

						my $t;
						eval {
							$t = $k->get_subkey("Properties\\{83da6326-97a6-4088-9453-a1923f573b29}\\0064")->get_value("")->get_data();
							my ($t0,$t1) = unpack("VV",$t);
							#append First InstallDate
							push(@arrayRow, ::getDateFromEpoch(::getTime($t0,$t1))."Z");
						};
						
						eval {
							$t = $k->get_subkey("Properties\\{83da6326-97a6-4088-9453-a1923f573b29}\\0065")->get_value("")->get_data();
							my ($t0,$t1) = unpack("VV",$t);
							#append InstallDate
							push(@arrayRow, ::getDateFromEpoch(::getTime($t0,$t1))."Z");
						};
						
						eval {
							$t = $k->get_subkey("Properties\\{83da6326-97a6-4088-9453-a1923f573b29}\\0066")->get_value("")->get_data();
							my ($t0,$t1) = unpack("VV",$t);
							#append LastArrival
							push(@arrayRow, ::getDateFromEpoch(::getTime($t0,$t1))."Z");
						};
						
						eval {
							$t = $k->get_subkey("Properties\\{83da6326-97a6-4088-9453-a1923f573b29}\\0067")->get_value("")->get_data();
							my ($t0,$t1) = unpack("VV",$t);
							#append LastRemoval
							push(@arrayRow, ::getDateFromEpoch(::getTime($t0,$t1))."Z");
						};
						
						push(@result, \@arrayRow);
					}
				}
				my $csv = Text::CSV->new({binary=>1, eol=>$/}) or die "cannot use CSV:".Text::CSV->error_diag();
				open my $fh,">:encoding(EUC-KR)", "usb.csv" or die "usb.csv: $!";
				
				for (@result){
				        $csv->print($fh, $_);
				}
				close $fh or die "usb.csv: $!";
			}
		}
		else {
			::rptMsg($key_path." has no subkeys.");
		}
	}
	else {
		::rptMsg($key_path." not found.");
	}
}
1;
