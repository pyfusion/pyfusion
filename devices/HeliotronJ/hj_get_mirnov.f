c *** program for loading data of mp fast samping            ***
c *** connection to IDL                                      *** 
c *** In the IDLprogram, you have to use "spawn, 'load_pmp'" ***
c *** programed by S. Yamamoto on Feb. 14, 2005              ***
c
      subroutine getmirnov (ishotno)
       implicit real (a-h,o-z)
cf2py intent(callback) getdata
       external getdata
c
c *** define array and parameter ***
      dimension dataary(14,262144),tary(262144)
c      dimension tary(262144)
      dimension tmpary(262144)
      integer iadc_bit,iampfilt,ishotno
      integer ibhv,ibta,ibtb,ibav,ibiv
      integer ich,isample,iswch
      integer ierror
      character*16 signalnm(14),modulenm
c      character*16 signalnm,modulenm
      character*100 paneldt
      character*21 datascl,dataunit
      character*6 stime
      character*9 sdate
c
c *** define signal name ***
      signalnm(1) ='PMP1'
      signalnm(2) ='PMP2'
      signalnm(3) ='PMP3'
      signalnm(4) ='PMP4'
      signalnm(5) ='PMP5'
      signalnm(6) ='PMP6'
      signalnm(7) ='PMP7'
      signalnm(8) ='PMP8'
      signalnm(9) ='PMP9'
      signalnm(10)='PMP10'
      signalnm(11)='PMP11'
      signalnm(12)='PMP12'
      signalnm(13)='PMP13'
      signalnm(14)='PMP14'
c
c *** read shot number from text ***
c      open(20, file='tmp_sn.dat') 
c      read(20, *) ishotno
c      close(20) 
      iswch=1
c
c *** load data ***
      do 100 i=1,14
      call getdata(signalnm(i),modulenm,paneldt,datascl,dataunit,sdate,
     &  stime,tmpary,tary,tsamp,tdelay,ampgain,sc_max,sc_min,bitzero,
     &  iadc_bit,iampfile,ishotno,ibhv,ibta,ibtb,ibav,ibiv,
     &  ich,isample,iswch,ierror)
        do 200 j=1,262144
            dataary(i,j) = tmpary(j)
  200   continue
  100 continue
c
c *** check error ***
      if(ierror.ne.0) write(6,*) 'MP data NOT found'
      if(ierror.eq.0) write(6,*) 'MP data found'
c
c *** write data ***
      open(21, file='tmp_data.dat',status='OLD')
      do 300 jt=1,262144
          write(21,*), tary(jt),(dataary(i,jt),i=1,14)
  300 continue
      close(21)
c      common /data/ iswch
c      print*, "iswch=",iswch
c
c *** stop program ***
      end
c
