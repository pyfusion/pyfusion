"""
H-1 specific utility code...
"""
from numpy import poly1d,polyval,array, ndarray, sin, cos
import pyfusion
from pyfusion.utils import remap_angle_0_2pi
from pyfusion.datamining.clustering.core import get_sin_cos_phase_for_channel_pairs, Cluster, FluctuationStructure,cluster_flucstrucs 
from pyfusion.devices.H1.H1 import H1Shot
# coefficients for 6th order polynomial mapping kappa_h to LCFS magnetic angle for each Mirnov coil
from sqlalchemy.sql import select

c1   = [-9.06397180e-05, 3.22626079e-04, -4.36408010e-04, 3.83230378e-01,-4.30402453e-01, 2.06079743e-01,-1.83250233e-01]
c2   = [-4.02284321e-04, 1.40334646e-03, -1.80544756e-03, 7.19490088e-01,-1.02622240e+00, 3.77580551e-01, 1.93965006e-01]
c3   = [-5.84432244e-04, 2.24320881e-03, -3.26986904e-03, 6.44645056e-01,-9.12644786e-01, 3.01457007e-01, 4.90844451e-01]
c4   = [ 0.00086943    ,-0.00276959    ,  0.0032095     , 0.01156458    , 0.1516046     ,-0.13496637    , 0.84333322    ]
c5   = [-4.20289652e-04, 1.48129243e-03, -1.92921916e-03,-6.77747879e-01, 1.13445396e+00,-3.68378362e-01, 1.10929753e+00]
c6   = [ 8.17030172e-05,-1.86807181e-04,  8.18193476e-05,-2.06419345e-01, 4.22036348e-01,-5.16587367e-04, 1.44790251e+00]
c7   = [ 2.68831288e-04,-9.55282368e-04,  1.24116142e-03, 3.70247982e-01,-3.96639385e-01, 3.17988920e-01, 1.63707736e+00]
c8   = [ 7.45254277e-04,-2.59151856e-03,  3.35602908e-03, 4.38443082e-01,-4.05292823e-01, 2.95786256e-01, 1.73255829e+00]
c9   = [-1.16430791e-04, 4.96534802e-05,  5.14299900e-04, 5.27268143e-01,-5.03374446e-01, 3.35157002e-01, 1.81087137e+00]
c10  = [ 3.84611067e-04,-1.28850018e-03,  1.52770699e-03, 6.04223508e-01,-5.23906629e-01, 3.41631063e-01, 1.94854143e+00]
c11  = [ 3.01533575e-04,-1.38440668e-03,  2.39254023e-03, 2.12455177e-01,-2.24702212e-02, 2.49246544e-01, 2.19661208e+00]
c12  = [-1.02060318e-03, 3.66267927e-03, -5.09179014e-03, 1.47407038e-01,-9.25444506e-02, 3.13187484e-01, 2.44197344e+00]
c13  = [ 5.43881558e-04,-2.00638312e-03,  2.85894379e-03, 1.84485681e-01,-2.14696383e-01, 3.68400592e-01, 2.59791234e+00]
c14  = [-2.66943593e-04, 1.01113150e-03, -1.43331757e-03, 3.31546512e-01,-5.45737127e-01, 4.88977254e-01, 2.78012394e+00]
c15  = [ 3.78902441e-04,-1.36226274e-03,  1.80556273e-03,-3.52685316e-01, 4.15052049e-01,-8.49717076e-02, 3.61336185e+00]
c16  = [ 1.06297061e-04,-2.63981141e-04,  1.65478186e-04,-2.77805243e-01, 2.10262049e-01, 1.73724544e-01, 4.09298339e+00]
c17  = [ 5.83045576e-04,-2.26613399e-03,  3.39577291e-03,-2.81267821e-01, 6.26330200e-01,-1.16454124e-01, 4.64750921e+00]
c18  = [ 2.45061595e-04,-5.88307108e-04,  3.77237716e-04, 3.06692588e-01,-3.31576525e-01, 3.56219098e-01, 5.12275280e+00]
c19  = [ 8.67632059e-05,-2.97881068e-04,  3.75913828e-04, 3.03048042e-01,-2.99618350e-01, 3.22164051e-01, 5.17794134e+00]
c20  = [ 3.80079703e-04,-1.54419795e-03,  2.36602703e-03, 1.81259730e-02, 2.38425436e-01,-8.83453041e-04, 5.58474261e+00]
# linear Mirnov array coefficients not great. Also, coils 1,3 are missing
clin2= [-0.37784254    , 0.28433464    ,  1.15695469    ,-1.54360094    , 0.81665523    ,-0.08443082    , 5.43522038    ]
clin4= [-9.48773181    ,29.19451503    ,-33.74617137    ,19.20484851    ,-5.82026837    , 0.97909598    , 5.53394061    ]
clin5= [ 1.50472658    ,-3.09129527    ,  1.19644928    , 0.98509875    ,-0.54059646    , 0.1423195     , 5.66701455    ]

coil_coef_mapping = {'mirnov_1_1':c1,
                     'mirnov_1_2':c2,
                     'mirnov_1_3':c3,
                     'mirnov_1_4':c4,
                     'mirnov_1_5':c5,
                     'mirnov_1_6':c6,
                     'mirnov_1_7':c7,
                     'mirnov_1_8':c8,
                     'mirnov_1_9':c9,
                     'mirnov_1_10':c10,
                     'mirnov_1_11':c11,
                     'mirnov_1_12':c12,
                     'mirnov_1_13':c13,
                     'mirnov_1_14':c14,
                     'mirnov_1_15':c15,
                     'mirnov_1_16':c16,
                     'mirnov_1_17':c17,
                     'mirnov_1_18':c18,
                     'mirnov_1_19':c19,
                     'mirnov_1_20':c20,
                     'mirnov_2_1':c1,
                     'mirnov_2_2':c2,
                     'mirnov_2_3':c3,
                     'mirnov_2_4':c4,
                     'mirnov_2_5':c5,
                     'mirnov_2_6':c6,
                     'mirnov_2_7':c7,
                     'mirnov_2_8':c8,
                     'mirnov_2_9':c9,
                     'mirnov_2_10':c10,
                     'mirnov_2_11':c11,
                     'mirnov_2_12':c12,
                     'mirnov_2_13':c13,
                     'mirnov_2_14':c14,
                     'mirnov_2_15':c15,
                     'mirnov_2_16':c16,
                     'mirnov_2_17':c17,
                     'mirnov_2_18':c18,
                     'mirnov_2_19':c19,
                     'mirnov_2_20':c20,
                     'mirnov_linear_2':clin2,
                     'mirnov_linear_4':clin4,
                     'mirnov_linear_5':clin5}

kh_mean_mag_angles = {}
kh_avg_limits = [0.0,1.2]
for ch in coil_coef_mapping.keys():
    lims = polyval(poly1d(coil_coef_mapping[ch]).integ(),kh_avg_limits)
    kh_mean_mag_angles[ch] = (lims[1]-lims[0])/(kh_avg_limits[1] - kh_avg_limits[0])


def map_kappa_h_mag_angle(kappa_h, coil_name):
    kh_angle_poly = poly1d(coil_coef_mapping[coil_name])
    return polyval(kh_angle_poly, kappa_h)


def map_phase_kh_avg(input_phase, kh, channel_1, channel_2):
    """
    take the phase between two channels and map it to the phase between the 
    corresponding kappa_h-averaged 'virtual' channels
    """
    c1_mag_angle = map_kappa_h_mag_angle(kh, channel_1)
    c2_mag_angle = map_kappa_h_mag_angle(kh, channel_2)
    scale_factor = (kh_mean_mag_angles[channel_2] - kh_mean_mag_angles[channel_1])/(c2_mag_angle - c1_mag_angle)
    return scale_factor*input_phase


def h1_khavg_fs_phases(fs_list, channel_pairs = None):
    """
    for a h-1 flucstrus, get the kh-avg delta_phases 
    if channel_pairs not supplied, will take neighbour coils 
    from diag ordered channels
    """
    if channel_pairs:
        raise NotImplementedError
    
    # this is a temporary hack: will be removed when dphase class is changed to use relations rather than id columns (which require further lookup)
    channels = pyfusion.session.query(pyfusion.Channel).all()
    ch_id_name_map = {}
    for ch in channels:
        ch_id_name_map[str(ch.id)] = ch.name
    output_phases = []
    for fs in fs_list:
        fs_dphases = []
        kh = fs.svd.timesegment.shot.kappa_h
        if len(fs.phases) == 0:
            print '...getting phases for flucstruc %d' %(fs.id)
            fs.get_phases()
        for dp in fs.phases:
            fs_dphases.append(map_phase_kh_avg(dp.d_phase, kh, ch_id_name_map[str(dp.channel_1_id)], ch_id_name_map[str(dp.channel_2_id)]))
        output_phases.append(fs_dphases)
        if pyfusion.settings.VERBOSE>5: print("%d fs_phases" % len(fs_dphases))
    return array(output_phases)


def get_h1_khavg_phases_for_cluster(cl):
    return h1_khavg_fs_phases(cl.flucstrucs)


def get_h1_khavg_sin_cos_phases_for_cluster(cl):
    cl_ph = h1_khavg_fs_phases(cl.flucstrucs)
    cl_cs_phases = ndarray(shape=(cl_ph.shape[0],2*cl_ph.shape[1]))
    cl_cs_phases[:,::2] = sin(cl_ph)
    cl_cs_phases[:,1::2] = cos(cl_ph)
    return cl_cs_phases


def get_kh_flucstuc_properties(cl,fs_props=['frequency']):
    joined_table = Cluster.__table__.join(cluster_flucstrucs).join(
        FluctuationStructure.__table__).join(pyfusion.MultiChannelSVD.__table__).join(pyfusion.TimeSegment.__table__).join(pyfusion.Shot.__table__).join(H1Shot.__table__)

    select_list = [H1Shot.kappa_h]
    for fs_p in fs_props:
        select_list.append(FluctuationStructure.__dict__[fs_p])

    data_select = select(select_list,from_obj=[joined_table]).where(
        Cluster.id==cl.id).group_by(FluctuationStructure.id) 

    data = pyfusion.session.execute(data_select).fetchall()

    return data

def get_kh_fs_freq(cl):
    return get_kh_flucstuc_properties(cl, fs_props=['frequency'])

def get_kappa_h(shot_number, time=None, average_interval=0.001, mdsserver='localhost'):
    """Return the kappa_h (helicalcurrent ratio) for H1 for a given shot
    if no time is given, return the programmed value.  Otherwise the measured.
    Used to live in examples, so that it does not require all of pyfusion.
    """
    import pmds
    pmds.mdsconnect(mdsserver)
    pmds.mdsopen('h1data', shot_number)
    im2 = pmds.mdsvalue('.operations.magnetsupply.lcu.setup_main.i2')
    is2 = pmds.mdsvalue('.operations.magnetsupply.lcu.setup_sec.i2')
    return is2/im2
