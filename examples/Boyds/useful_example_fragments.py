from pyfusion.datamining.clustering.utils import get_fs_for_shot
fs_list=get_fs_for_shot(58060, time_range=[0.039,0.041])
plot_bar_fs_list(fs_list)
plot_bar_fs_list(fs_list,orientation='horizontal',hold=0)

for fs in fs_list: print("Fr=%.3gkHz, En=%.3g, a12=%.3g, a1=%.3g" % (fs.frequency/1e3, fs.energy, fs.a12, fs.a1))

bar(arange(len(fs_list)),[fs.a1 for fs in fs_list])
bar(arange(len(fs_list)),[fs.a1*fs.a12 for fs in fs_list],color='c')
bar(arange(len(fs_list)),[fs.a1*fs.a13 for fs in fs_list],color='y')

select _chrono from svs order by svd_id asc limit 1;
select shot,proc_date from shots;
select count(*) from dm_fs where energy<0.1 or (energy<0.3 and a12=0);
select device_id, min(shot),max(shot), max(svds.normalised) from shots, svds limit 4;
